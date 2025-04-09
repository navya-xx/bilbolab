import multiprocessing as mp
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import queue  # For queue.Empty exceptions

# === CUSTOM PACKAGES ==================================================================================================
from core.utils.callbacks import callback_definition, CallbackContainer


# ======================================================================================================================
class UpdatablePlotProcess(mp.Process):
    def __init__(self, command_queue, event_queue, x_label="X", y_label="Y", xlim=None, ylim=None, common_x=None):
        super().__init__()
        self.command_queue = command_queue
        self.event_queue = event_queue  # Used to notify main process of events (e.g. close)
        self.x_label = x_label
        self.y_label = y_label
        self.xlim = xlim
        self.ylim = ylim
        self.common_x = common_x

    def run(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        if self.xlim is not None:
            self.ax.set_xlim(self.xlim)
        if self.ylim is not None:
            self.ax.set_ylim(self.ylim)
        if self.common_x is not None:
            self.ax.set_xticks(self.common_x)

        self.lines = []
        self.fig.show()
        self.fig.canvas.draw()
        self.ax.grid()

        # Register a close-event handler in the GUI process.
        def handle_close(event):
            self.event_queue.put({'event': 'close'})

        self.fig.canvas.mpl_connect('close_event', handle_close)

        # Main loop: poll for commands and process GUI events.
        while True:
            while not self.command_queue.empty():
                cmd = self.command_queue.get()
                if cmd['command'] == 'append':
                    x = cmd['x']
                    y = cmd['y']
                    color = cmd['color']
                    label = cmd['label']
                    line, = self.ax.plot(x, y, color=color, label=label)
                    self.lines.append(line)
                    handles, labels = self.ax.get_legend_handles_labels()
                    if handles:
                        self.ax.legend()
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
                elif cmd['command'] == 'remove':
                    if cmd.get('last', False):
                        if self.lines:
                            line = self.lines.pop()
                            line.remove()
                    elif 'index' in cmd:
                        idx = cmd['index']
                        if 0 <= idx < len(self.lines):
                            line = self.lines.pop(idx)
                            line.remove()
                    handles, labels = self.ax.get_legend_handles_labels()
                    if handles:
                        self.ax.legend()
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
                elif cmd['command'] == 'close':
                    plt.close(self.fig)
                    return
            plt.pause(0.1)


# ======================================================================================================================
@callback_definition
class UpdatablePlotCallbacks:
    close: CallbackContainer


# ======================================================================================================================
class UpdatablePlot:
    """
    A proxy class that communicates with the plotting process for static/updatable plots.
    """

    def __init__(self, x_label="X", y_label="Y", xlim=None, ylim=None, common_x=None):
        self.command_queue = mp.Queue()
        self.event_queue = mp.Queue()  # Event queue for detecting GUI events from the process.
        self.plot_process = UpdatablePlotProcess(self.command_queue, self.event_queue,
                                                 x_label, y_label, xlim, ylim, common_x)
        self.plot_process.start()
        self.callbacks = UpdatablePlotCallbacks()

        # Start an event listener thread in the main process.
        self._event_listener_thread = threading.Thread(target=self._event_listener, daemon=True)
        self._event_listener_thread.start()

    def _event_listener(self):
        while True:
            try:
                event = self.event_queue.get(timeout=0.1)
                if event.get('event') == 'close':
                    self.on_close()
                    break
            except queue.Empty:
                continue

    def on_close(self):
        self.callbacks.close.call()

    def appendPlot(self, x, y, color=None, label=None):
        self.command_queue.put({
            'command': 'append',
            'x': x,
            'y': y,
            'color': color,
            'label': label
        })

    def removePlot(self, index=None, last=False):
        if last:
            self.command_queue.put({'command': 'remove', 'last': True})
        elif index is not None:
            self.command_queue.put({'command': 'remove', 'index': index})
        else:
            print("Please provide an index or set last=True to remove a plot.")

    def close(self, *args, **kwargs):
        self.command_queue.put({'command': 'close'})
        self.plot_process.join()


# ======================================================================================================================
@callback_definition
class RealTimePlotCallbacks:
    close: CallbackContainer


# NEW: Separate process class for the RealTimePlot.
class RealTimePlotProcess(mp.Process):
    def __init__(self, data_queue, control_queue, event_queue,
                 window_length, signals_info, value_format, title):
        super().__init__()
        self.data_queue = data_queue
        self.control_queue = control_queue
        self.event_queue = event_queue
        self.window_length = window_length
        self.signals_info = signals_info
        self.value_format = value_format
        self.title = title
        self.num_signals = len(signals_info)

    def run(self):
        times = []
        values = [[] for _ in range(self.num_signals)]
        fig = plt.figure(figsize=(10, 6))
        main_ax = fig.add_subplot(111)
        if self.title:
            main_ax.set_title(self.title)
        axes = [main_ax]

        # For additional signals, create twin axes.
        if self.num_signals > 1:
            for i in range(1, self.num_signals):
                new_ax = main_ax.twinx()
                new_ax.spines["right"].set_position(("outward", 60 * (i - 1)))
                axes.append(new_ax)

        for i, ax in enumerate(axes):
            ax.set_ylim(self.signals_info[i]["ymin"], self.signals_info[i]["ymax"])
            ax.set_ylabel(self.signals_info[i]["name"])
        main_ax.set_xlabel("Time (s)")
        main_ax.grid()

        lines = []
        color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        for i in range(self.num_signals):
            line, = axes[i].plot([], [],
                                 color=color_cycle[i % len(color_cycle)],
                                 label=self.signals_info[i]["name"])
            lines.append(line)
        main_ax.legend(loc="upper left")

        texts = []
        for i in range(self.num_signals):
            x_pos = 0.1 + i * 0.3
            txt = fig.text(x_pos, 0.02, "", fontfamily="monospace", fontsize=14)
            texts.append(txt)

        def update_plot(frame):
            # Process all new data.
            while not self.data_queue.empty():
                try:
                    t, vals = self.data_queue.get_nowait()
                    times.append(t)
                    for i in range(self.num_signals):
                        values[i].append(vals[i])
                    # Remove old data outside the rolling window.
                    while times and times[0] < t - self.window_length:
                        times.pop(0)
                        for v in values:
                            v.pop(0)
                except Exception:
                    break

            # Process any control commands.
            try:
                while True:
                    cmd = self.control_queue.get_nowait()
                    if cmd.get('command') == 'close':
                        plt.close(fig)
                        return
            except queue.Empty:
                pass

            if not times:
                return

            current_time = times[-1]
            for i, line in enumerate(lines):
                line.set_data(times, values[i])
            axes[0].set_xlim(current_time - self.window_length, current_time)

            fixed_width = 7  # Fixed width formatting for displayed values.
            for i, txt in enumerate(texts):
                if values[i]:
                    current_val = values[i][-1]
                    formatted_val = f"{current_val:{fixed_width}{self.value_format}}"
                    txt.set_text(f"{self.signals_info[i]['name']}: {formatted_val}")

            fig.canvas.draw_idle()

        def handle_close(event):
            self.event_queue.put({'event': 'close'})

        fig.canvas.mpl_connect('close_event', handle_close)

        ani = animation.FuncAnimation(fig, update_plot, interval=100, frames=20)
        while plt.fignum_exists(fig.number):
            plt.pause(0.1)


# ======================================================================================================================
class RealTimePlot:
    """
    A real-time rolling plot for timeseries data.
    """

    def __init__(self, window_length, signals_info, value_format=".2f", title=None):
        self.window_length = window_length
        self.signals_info = signals_info
        self.value_format = value_format
        self.title = title
        self.num_signals = len(signals_info)
        self.start_time = 0

        self.data_queue = mp.Queue()
        self.control_queue = mp.Queue()
        self.event_queue = mp.Queue()
        self.proc = None

        self.callbacks = RealTimePlotCallbacks()
        self._event_listener_thread = threading.Thread(target=self._event_listener, daemon=True)
        self._event_listener_thread.start()

    def _event_listener(self):
        while True:
            try:
                event = self.event_queue.get(timeout=0.1)
                if event.get('event') == 'close':
                    self.on_close()
                    break
            except queue.Empty:
                continue

    def on_close(self):
        self.callbacks.close.call()

    def start(self):
        self.proc = RealTimePlotProcess(
            data_queue=self.data_queue,
            control_queue=self.control_queue,
            event_queue=self.event_queue,
            window_length=self.window_length,
            signals_info=self.signals_info,
            value_format=self.value_format,
            title=self.title
        )
        self.proc.daemon = True
        self.proc.start()
        self.start_time = time.time()

    def close(self):
        if self.proc is not None:
            self.control_queue.put({'command': 'close'})
            self.proc.join()

    def push_data(self, values):
        if not isinstance(values, list):
            values = [values]
        timestamp = time.time() - self.start_time
        self.data_queue.put((timestamp, values))


# ======================================================================================================================
# Test functions demonstrating the functionality.
def testUpdatablePlot():
    """
    Demonstrates the static/updatable plot by appending and removing curves.
    """
    up = UpdatablePlot(x_label="Time", y_label="Value", xlim=(0, 10), ylim=(-1, 1))
    up.callbacks.close.register(function=lambda: print("UpdatablePlot: Plot window closed callback triggered."))
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    up.appendPlot(x, y1, color='blue', label='sin')
    time.sleep(2)
    y2 = np.cos(x)
    up.appendPlot(x, y2, color='red', label='cos')
    time.sleep(2)
    up.removePlot(index=0)
    time.sleep(2)
    up.removePlot(last=True)
    time.sleep(2)
    up.close()


def testRealTimePlot():
    """
    Demonstrates the real-time rolling plot by pushing random data.
    """
    signals_info = [
        {"name": "Signal 1", "ymin": -1, "ymax": 1},
        {"name": "Signal 2", "ymin": 0, "ymax": 10}
    ]
    rt = RealTimePlot(window_length=10, signals_info=signals_info, title="Real-Time Plot")
    rt.callbacks.close.register(function=lambda: print("RealTimePlot: Plot window closed callback triggered."))
    rt.start()
    start_time = time.time()
    while time.time() - start_time < 15:
        data1 = np.sin(time.time())
        data2 = np.random.random() * 10
        rt.push_data([data1, data2])
        time.sleep(0.1)
    rt.close()


if __name__ == "__main__":
    print("Testing UpdatablePlot...")
    testUpdatablePlot()
    time.sleep(1)
    print("Testing RealTimePlot...")
    testRealTimePlot()

# import matplotlib.pyplot as plt
# import time
# import numpy as np
#
#
# class UpdatablePlot:
#     def __init__(self, x_label="X", y_label="Y", xlim=None, ylim=None, common_x=None, grid=True):
#         # Enable interactive mode so that the plot updates dynamically.
#         plt.ion()
#         self.fig, self.ax = plt.subplots()
#         self.ax.set_xlabel(x_label)
#         self.ax.set_ylabel(y_label)
#
#         if xlim is not None:
#             self.ax.set_xlim(xlim)
#         if ylim is not None:
#             self.ax.set_ylim(ylim)
#
#         # If a common x-vector is provided, set the x-ticks accordingly.
#         if common_x is not None:
#             self.ax.set_xticks(common_x)
#
#         # List to keep track of plot line objects.
#         self.lines = []
#
#         # Show the (initially empty) plot.
#         self.fig.show()
#         self.fig.canvas.draw()
#
#         if grid:
#             self.ax.grid()
#
#     def appendPlot(self, x, y, color, label):
#         """
#         Appends a new curve to the plot.
#         Parameters:
#             x (array-like): x-data for the plot.
#             y (array-like): y-data for the plot.
#             color (str): Color of the plot line.
#             label (str): Label for the plot line.
#         """
#         line, = self.ax.plot(x, y, color=color, label=label)
#         self.lines.append(line)
#         self.ax.legend()
#         self.fig.canvas.draw()
#         self.fig.canvas.flush_events()
#
#     def removePlot(self, index=None, last=False):
#         """
#         Removes a plot line from the figure.
#         Parameters:
#             index (int, optional): The index of the plot to remove.
#             last (bool, optional): If True, removes the last plot.
#         """
#         if last:
#             if self.lines:
#                 line = self.lines.pop()
#                 line.remove()
#         elif index is not None:
#             if 0 <= index < len(self.lines):
#                 line = self.lines.pop(index)
#                 line.remove()
#         else:
#             print("Please provide an index or set last=True to remove a plot.")
#             return
#
#         handles, labels = self.ax.get_legend_handles_labels()
#         if handles:
#             self.ax.legend()
#         self.fig.canvas.draw()
#         self.fig.canvas.flush_events()
#
#
# def testUpdatablePlot():
#     # Create an updatable plot with custom x and y labels and axis limits.
#     up = UpdatablePlot(x_label="Time", y_label="Value", xlim=(0, 10), ylim=(-1, 1))
#
#     # Create a common x-axis vector.
#     x = np.linspace(0, 10, 100)
#
#     # Add first plot: sine curve.
#     y1 = np.sin(x)
#     up.appendPlot(x, y1, color='blue', label='sin')
#     time.sleep(2)  # Pause for 2 seconds so we can see the update.
#
#     # Add second plot: cosine curve.
#     y2 = np.cos(x)
#     up.appendPlot(x, y2, color='red', label='cos')
#     time.sleep(2)
#
#     # Remove the first plot (sine curve) by index.
#     up.removePlot(index=0)
#     time.sleep(2)
#
#     # Remove the last plot (cosine curve).
#     up.removePlot(last=True)
#     time.sleep(2)
#
#     # Turn off interactive mode and show the final state (if any).
#     plt.ioff()
#     plt.show()
#
#
# if __name__ == "__main__":
#     testUpdatablePlot()


import multiprocessing as mp
import matplotlib.pyplot as plt
import numpy as np
import time


class UpdatablePlotProcess(mp.Process):
    def __init__(self, command_queue, x_label="X", y_label="Y", xlim=None, ylim=None, common_x=None):
        super().__init__()
        self.command_queue = command_queue
        self.x_label = x_label
        self.y_label = y_label
        self.xlim = xlim
        self.ylim = ylim
        self.common_x = common_x

    def run(self):
        # Enable interactive mode in this process.
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

        # List to keep track of added plot lines.
        self.lines = []

        self.fig.show()
        self.fig.canvas.draw()
        self.ax.grid()

        # Main loop for the plotting process.
        while True:
            # Process all commands in the queue.
            while not self.command_queue.empty():
                cmd = self.command_queue.get()
                if cmd['command'] == 'append':
                    # Add a new plot line.
                    x = cmd['x']
                    y = cmd['y']
                    color = cmd['color']
                    label = cmd['label']
                    line, = self.ax.plot(x, y, color=color, label=label)
                    self.lines.append(line)
                    # Update the legend only if there are valid handles.
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
                    # Update the legend (suppressing the warning by checking if any handles exist).
                    handles, labels = self.ax.get_legend_handles_labels()
                    if handles:
                        self.ax.legend()
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
                elif cmd['command'] == 'close':
                    plt.close(self.fig)
                    return  # Exit the process

            # Allow GUI event processing.
            plt.pause(0.1)


class UpdatablePlot:
    """
    A proxy class that communicates with the plotting process.
    """

    def __init__(self, x_label="X", y_label="Y", xlim=None, ylim=None, common_x=None):
        self.command_queue = mp.Queue()
        self.plot_process = UpdatablePlotProcess(self.command_queue, x_label, y_label, xlim, ylim, common_x)
        self.plot_process.start()

    def appendPlot(self, x, y, color, label):
        """
        Send a command to append a new plot line.
        """
        self.command_queue.put({
            'command': 'append',
            'x': x,
            'y': y,
            'color': color,
            'label': label
        })

    def removePlot(self, index=None, last=False):
        """
        Send a command to remove a plot line.
        """
        if last:
            self.command_queue.put({
                'command': 'remove',
                'last': True
            })
        elif index is not None:
            self.command_queue.put({
                'command': 'remove',
                'index': index
            })
        else:
            print("Please provide an index or set last=True to remove a plot.")

    def close(self):
        """
        Cleanly close the plotting process.
        """
        self.command_queue.put({'command': 'close'})
        self.plot_process.join()


def testUpdatablePlot():
    """
    Demonstrates the functionality by appending and removing plots with delays.
    """
    # Create the updatable plot.
    up = UpdatablePlot(x_label="Time", y_label="Value", xlim=(0, 10), ylim=(-1, 1))

    # Create a common x-axis vector.
    x = np.linspace(0, 10, 100)

    # Append a sine curve.
    y1 = np.sin(x)
    up.appendPlot(x, y1, color='blue', label='sin')
    time.sleep(2)  # Wait 2 seconds

    # Append a cosine curve.
    y2 = np.cos(x)
    up.appendPlot(x, y2, color='red', label='cos')
    time.sleep(2)

    # Remove the first plot by index.
    up.removePlot(index=0)
    time.sleep(2)

    # Remove the last plot.
    up.removePlot(last=True)
    time.sleep(2)

    # Close the plotting process.
    up.close()


if __name__ == "__main__":
    testUpdatablePlot()

import math
import threading
import time

from extensions.joystick.joystick_manager import Joystick
from robots.bilbo.robot.bilbo_control import BILBO_Control
from robots.bilbo.robot.bilbo_core import BILBO_Core
from robots.bilbo.robot.bilbo_definitions import BILBO_Control_Mode
from robots.bilbo.robot.utils.twipr_data import twiprSampleFromDict, BILBO_STATE_DATA_DEFINITIONS
from core.utils.callbacks import CallbackContainer, callback_definition, Callback
from core.utils.events import event_definition, ConditionEvent
from core.utils.plotting import RealTimePlot
from core.utils.exit import ExitHandler


# ======================================================================================================================
@callback_definition
class BILBO_Interfaces_Callbacks:
    joystick_connected: CallbackContainer
    joystick_disconnected: CallbackContainer


@event_definition
class BILBO_Interfaces_Events:
    joystick_connected: ConditionEvent
    joystick_disconnected: ConditionEvent


# ======================================================================================================================
class BILBO_Interfaces:
    joystick: (Joystick, None)
    live_plots: list[dict]

    joystick_thread: (threading.Thread, None)
    _exit_joystick_thread: bool

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, core: BILBO_Core, control: BILBO_Control):
        self.core = core
        self.control = control
        self.core.events.stream.on(self._streamCallback)

        self.live_plots = []
        self.joystick = None
        self.joystick_thread = None

        self._exit_joystick_thread = False

        self.exit = ExitHandler()
        self.exit.register(self.close)

    # ------------------------------------------------------------------------------------------------------------------
    def close(self, *args, **kwargs):
        self.removeJoystick()
        self.closeLivePlots()

    # ------------------------------------------------------------------------------------------------------------------
    def addJoystick(self, joystick: Joystick):

        self.core.logger.info("Add Joystick")

        self.joystick = joystick
        self.joystick.events.button.on(self.core.events.resume.set, flags={'button': 'DPAD_RIGHT'})
        self.joystick.events.button.on(self.core.events.revert.set, flags={'button': 'DPAD_LEFT'})

        self.joystick.events.button.on(Callback(self.control.enableTIC,
                                                inputs={'state': True}), flags={'button': 'DPAD_UP'})

        self.joystick.events.button.on(Callback(self.control.enableTIC,
                                                inputs={'state': False}), flags={'button': 'DPAD_DOWN'})

        self.joystick.events.button.on(Callback(self.control.setControlMode,
                                                inputs={'mode': BILBO_Control_Mode.BALANCING}),
                                       flags={'button': 'A'})

        self.joystick.events.button.on(Callback(self.control.setControlMode,
                                                inputs={'mode': BILBO_Control_Mode.OFF}),
                                       flags={'button': 'B'})

        self.joystick.events.button.on(callback=self.core.beep, flags={'button': 'X'})

        self._startJoystickThread()

    # ------------------------------------------------------------------------------------------------------------------
    def removeJoystick(self):

        self.core.logger.info("Remove Joystick")

        if self.joystick is not None:
            self.joystick.clearAllButtonCallbacks()
            self.joystick = None

        if self.joystick_thread is not None and self.joystick_thread.is_alive():
            self._exit_joystick_thread = True
            self.joystick_thread.join()
            self.joystick_thread = None

    # ------------------------------------------------------------------------------------------------------------------
    def openLivePlot(self, state_name: str):
        if state_name not in BILBO_STATE_DATA_DEFINITIONS:
            self.core.logger.error(f"State '{state_name}' not a valid state name.")
            return

        # Check if we already have a live plot with this state
        for live_plot in self.live_plots:
            if live_plot["state_name"] == state_name:
                self.core.logger.warning(f"Live plot for state '{state_name}' already exists.")
                return

        plot = RealTimePlot(window_length=10,
                            signals_info=[
                                {"name": state_name, "ymin": BILBO_STATE_DATA_DEFINITIONS[state_name]['min'],
                                 "ymax": BILBO_STATE_DATA_DEFINITIONS[state_name]['max']}],
                            title=f"{self.core.id}: {state_name}",
                            value_format=BILBO_STATE_DATA_DEFINITIONS[state_name]['display_resolution'])

        plot.callbacks.close.register(self._livePlotClosed_callback, inputs={"plot": plot})

        self.live_plots.append({
            "state_name": state_name,
            "plot": plot
        })

    # ------------------------------------------------------------------------------------------------------------------
    def closeLivePlots(self, state_name: str = None):

        if state_name is None:

            # Close all live plots
            live_plots = self.live_plots.copy()
            for live_plot in live_plots:
                live_plot["plot"].close()
                self.live_plots.remove(live_plot)
                self.core.logger.info(f"Closed live plot: {live_plot['state_name']}")

        else:
            for live_plot in self.live_plots:
                if live_plot["state_name"] == state_name:
                    live_plot["plot"].close()
                    self.live_plots.remove(live_plot)
                    self.core.logger.info(f"Closed live plot: {live_plot['state_name']}")
                    break

    # ------------------------------------------------------------------------------------------------------------------
    def _streamCallback(self, stream, *args, **kwargs):
        data = twiprSampleFromDict(stream.data)

        for plot in self.live_plots:
            state_name = plot["state_name"]
            state_data = getattr(data.estimation.state, plot[state_name])
            if BILBO_STATE_DATA_DEFINITIONS[state_name]['unit'] == 'rad':
                state_data = math.degrees(state_data)
            elif BILBO_STATE_DATA_DEFINITIONS[state_name]['unit'] == 'rad/s':
                state_data = math.degrees(state_data)
            plot["plot"].push_data(state_data)

    # ------------------------------------------------------------------------------------------------------------------
    def _livePlotClosed_callback(self, plot, *args, **kwargs):

        for live_plot in self.live_plots:
            if live_plot["plot"] == plot:
                self.live_plots.remove(live_plot)
                self.core.logger.info(f"Closed live plot: {live_plot['state_name']}")
                break

    # ------------------------------------------------------------------------------------------------------------------
    def _startJoystickThread(self):
        self.joystick_thread = threading.Thread(target=self._joystick_task, daemon=True)
        self.joystick_thread.start()
        self.core.logger.debug(
            f"Joystick thread started for {self.core.id}."
        )

    # ------------------------------------------------------------------------------------------------------------------
    def _joystick_task(self):
        self._exit_joystick_thread = False
        while not self._exit_joystick_thread:
            ...
            time.sleep(0.1)


# === TEST RESPONSE TIME ===============================================================================================
def test_response_time(bilbo, iterations=10, print_response_time=False):
    """
    Measures the response time of the Frodo robot's test method over multiple iterations.

    Args:
        frodo (Frodo): The Frodo robot instance.
        iterations (int, optional): Number of test iterations. Defaults to 10.
        print_response_time (bool, optional): Whether to print individual response times. Defaults to False.

    Logs:
        - Total number of timeouts.
        - Maximum, minimum, and average response times in milliseconds.
    """
    response_times: list[(None, float)] = [None] * iterations  # List to store response times
    timeouts = 0  # Counter for timeouts

    bilbo.logger.info("Testing response time")

    # Perform an initial write to check if the robot responds
    data = bilbo.test("HALLO", timeout=1)

    if data is None:
        bilbo.logger.warning("Initial write timed out")
        return  # Exit the function if initial test fails

    for i in range(iterations):
        start = time.perf_counter()  # Record start time
        data = bilbo.test("HALLO", timeout=1)  # Send test message

        if data is None:
            timeouts += 1  # Increment timeout counter
            response_times[i] = None
        else:
            response_times[i] = time.perf_counter() - start  # Calculate response time

        # Log response time or timeout occurrence
        if print_response_time and data is not None:
            bilbo.logger.info(f"{i + 1}/{iterations} Response time: {(response_times[i] * 1000):.2f} ms")
        else:
            bilbo.logger.warning(f"{i + 1}/{iterations} Timeout")

        time.sleep(0.25)  # Delay before next test iteration

    # Filter out None values (timeouts) from response times
    valid_times = [response_time for response_time in response_times if response_time is not None]

    # Calculate statistics
    max_time = max(valid_times)  # Maximum response time
    min_time = min(valid_times)  # Minimum response time
    avg_time = sum(valid_times) / len(valid_times)  # Average response time

    # Log results
    bilbo.logger.info(f"Timeouts: {timeouts}")
    bilbo.logger.info(f"Max time: {max_time * 1000:.2f} ms")
    bilbo.logger.info(f"Min time: {min_time * 1000:.2f} ms")
    bilbo.logger.info(f"Average time: {avg_time * 1000:.2f} ms")

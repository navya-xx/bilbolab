import math
import threading
import time

# === CUSTOM PACKAGES ==================================================================================================
from core.utils.sound.sound import speak
from extensions.cli.src.cli import CommandSet, Command, CommandArgument
from extensions.joystick.joystick_manager import Joystick
from robots.bilbo.robot.bilbo_control import BILBO_Control
from robots.bilbo.robot.bilbo_core import BILBO_Core
from robots.bilbo.robot.bilbo_definitions import BILBO_Control_Mode
from robots.bilbo.robot.bilbo_data import twiprSampleFromDict, BILBO_STATE_DATA_DEFINITIONS
from core.utils.callbacks import CallbackContainer, callback_definition, Callback
from core.utils.events import event_definition, ConditionEvent
from core.utils.plotting import RealTimePlot
from core.utils.exit import register_exit_callback

# ======================================================================================================================

JOYSTICK_UPDATE_TIME = 0.05


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

        register_exit_callback(self.close)

    # ------------------------------------------------------------------------------------------------------------------
    def close(self, *args, **kwargs):
        self.removeJoystick()
        self.closeLivePlots()

    # ------------------------------------------------------------------------------------------------------------------
    def addJoystick(self, joystick: Joystick):

        self.core.logger.info("Add Joystick")
        speak(f"Joystick {joystick.id} assigned to {self.core.id}")

        self.joystick = joystick
        self.joystick.events.button.on(self.core.interface_events.resume.set, flags={'button': 'DPAD_RIGHT'},
                                       input_resource=False)
        self.joystick.events.button.on(self.core.interface_events.revert.set, flags={'button': 'DPAD_LEFT'},
                                       input_resource=False)

        self.joystick.events.button.on(Callback(self.control.enableTIC,
                                                inputs={'state': True},
                                                discard_inputs=True), flags={'button': 'DPAD_UP'}, input_resource=False)

        self.joystick.events.button.on(Callback(self.control.enableTIC,
                                                inputs={'state': False},
                                                discard_inputs=True), flags={'button': 'DPAD_DOWN'},
                                       input_resource=False)

        self.joystick.events.button.on(Callback(self.control.setControlMode,
                                                inputs={'mode': BILBO_Control_Mode.BALANCING},
                                                discard_inputs=True),
                                       flags={'button': 'A'}, input_resource=False)

        self.joystick.events.button.on(Callback(self.control.setControlMode,
                                                inputs={'mode': BILBO_Control_Mode.OFF},
                                                discard_inputs=True),
                                       flags={'button': 'B'})

        self.joystick.events.button.on(callback=self.core.beep, flags={'button': 'X'}, input_resource=False)

        self._startJoystickThread()

    # ------------------------------------------------------------------------------------------------------------------
    def removeJoystick(self):
        if self.joystick is not None:
            self.core.logger.info("Remove Joystick")
            speak(f"Joystick {self.joystick.id} removed from {self.core.id}")
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

        if BILBO_STATE_DATA_DEFINITIONS[state_name]['unit'] == 'rad':
            min_val = math.degrees(BILBO_STATE_DATA_DEFINITIONS[state_name]['min'])
        else:
            min_val = BILBO_STATE_DATA_DEFINITIONS[state_name]['min']

        if BILBO_STATE_DATA_DEFINITIONS[state_name]['unit'] == 'rad':
            max_val = math.degrees(BILBO_STATE_DATA_DEFINITIONS[state_name]['max'])
        else:
            max_val = BILBO_STATE_DATA_DEFINITIONS[state_name]['max']

        plot = RealTimePlot(window_length=10,
                            signals_info=[
                                {"name": state_name, "ymin": min_val,
                                 "ymax": max_val}],
                            title=f"{self.core.id}: {state_name}",
                            value_format=BILBO_STATE_DATA_DEFINITIONS[state_name]['display_resolution'])

        plot.start()

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
            state_data = getattr(data.estimation.state, state_name)
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
        self.core.logger.info(
            f"Joystick thread started for {self.core.id}."
        )

    # ------------------------------------------------------------------------------------------------------------------
    def _joystick_task(self):
        self._exit_joystick_thread = False
        while not self._exit_joystick_thread:
            forward_joystick = -self.joystick.getAxis('LEFT_VERTICAL')
            turn_joystick = -self.joystick.getAxis('RIGHT_HORIZONTAL')

            # if self.control.mode == BILBO_Control_Mode.BALANCING:
            self.control.setNormalizedBalancingInput(forward_joystick, turn_joystick)

            time.sleep(JOYSTICK_UPDATE_TIME)


# ======================================================================================================================
class BILBO_CLI_CommandSet(CommandSet):

    def __init__(self, robot: 'BILBO'):
        self.robot = robot

        beep_command = Command(name='beep',
                               callback=self.robot.core.beep,
                               allow_positionals=True,
                               arguments=[
                                   CommandArgument(name='frequency',
                                                   type=int,
                                                   short_name='f',
                                                   description='Frequency of the beep',
                                                   is_flag=False,
                                                   optional=True,
                                                   default=700),
                                   CommandArgument(name='time_ms',
                                                   type=int,
                                                   short_name='t',
                                                   description='Time of the beep in milliseconds',
                                                   is_flag=False,
                                                   optional=True,
                                                   default=250),
                                   CommandArgument(name='repeats',
                                                   type=int,
                                                   short_name='r',
                                                   description='Number of repeats',
                                                   is_flag=False,
                                                   optional=True,
                                                   default=1)
                               ],
                               description='Beeps the Buzzer')

        speak_command = Command(name='speak',
                                callback=self.robot.speak,
                                allow_positionals=True,
                                arguments=[
                                    CommandArgument(name='text',
                                                    type=str,
                                                    short_name='t',
                                                    description='Text to speak',
                                                    is_flag=False,
                                                    optional=True,
                                                    default=None)
                                ], )

        mode_command = Command(name='mode',
                               callback=self.robot.control.setControlMode,
                               allow_positionals=True,
                               arguments=[
                                   CommandArgument(name='mode',
                                                   type=int,
                                                   short_name='m',
                                                   description='Mode of control (0:off, 1:direct, 2:torque)',
                                                   is_flag=False,
                                                   optional=False,
                                                   default=None)
                               ], )

        stop_command = Command(name='stop',
                               callback=self.robot.stop,
                               description='Deactivates the control on the robot',
                               arguments=[])

        read_state_command = Command(name='read',
                                     callback=self.robot.control.getControlState,
                                     description='Reads the current control state and mode', )

        test_communication = Command(name='testComm',
                                     callback=self.test_communication,
                                     description='Tests the communication with the robot',
                                     arguments=[
                                         CommandArgument(name='iterations',
                                                         short_name='i',
                                                         type=int,
                                                         optional=True,
                                                         default=10,
                                                         description='Number of iterations to test')
                                     ])

        statefeedback_command = Command(name='sfg',
                                        callback=self.robot.control.setStateFeedbackGain,
                                        allow_positionals=True,
                                        arguments=[
                                            CommandArgument(name='gain',
                                                            type=list[float],
                                                            array_size=8,
                                                            short_name='g',
                                                            description='State feedback gain',
                                                            )
                                        ], )

        forward_pid_command = Command(name='fpid',
                                      callback=self.robot.control.setForwardPID,
                                      allow_positionals=True,
                                      arguments=[
                                          CommandArgument(name='p',
                                                          type=float,
                                                          short_name='p',
                                                          description='Forward PID P',
                                                          ),
                                          CommandArgument(name='i',
                                                          type=float,
                                                          short_name='i',
                                                          description='Forward PID I',
                                                          ),
                                          CommandArgument(name='d',
                                                          type=float,
                                                          short_name='d',
                                                          description='Forward PID D',
                                                          ),
                                      ], )

        turn_pid_command = Command(name='tpid',
                                   allow_positionals=True,
                                   callback=self.robot.control.setTurnPID,
                                   arguments=[
                                       CommandArgument(name='p',
                                                       type=float,
                                                       short_name='p',
                                                       description='Turn PID P',
                                                       ),
                                       CommandArgument(name='i',
                                                       type=float,
                                                       short_name='i',
                                                       description='Turn PID I',
                                                       ),
                                       CommandArgument(name='d',
                                                       type=float,
                                                       short_name='d',
                                                       description='Turn PID D',
                                                       ),
                                   ])

        read_control_config_command = Command(name='read',
                                              callback=self.robot.control.readControlConfiguration,
                                              description='Reads the current control configuration',
                                              arguments=[])

        control_command_set = CommandSet(name='control', commands=[
            statefeedback_command,
            forward_pid_command,
            turn_pid_command,
            read_control_config_command,
        ])

        test_trajectory_command = Command(name='test',
                                          allow_positionals=True,
                                          callback=self.robot.experiments.runTestTrajectories,
                                          execute_in_thread=True,
                                          arguments=[
                                              CommandArgument(name='num',
                                                              short_name='n',
                                                              type=int,
                                                              description='Number of trajectories',
                                                              optional=False,
                                                              ),
                                              CommandArgument(name='time',
                                                              short_name='t',
                                                              type=float,
                                                              description='Time to run the trajectory',
                                                              optional=False, ),
                                              CommandArgument(name='frequency',
                                                              short_name='f',
                                                              type=float,
                                                              description='Frequency of the Input',
                                                              optional=True,
                                                              default=3),
                                              CommandArgument(name='gain',
                                                              short_name='g',
                                                              type=float,
                                                              description='Gain of the Input',
                                                              optional=True,
                                                              default=0.1),
                                          ])

        experiment_command_set = CommandSet(name='experiment', commands=[test_trajectory_command])

        super().__init__(name=f"{robot.id}", commands=[beep_command,
                                                       speak_command,
                                                       mode_command,
                                                       stop_command,
                                                       read_state_command,
                                                       test_communication],

                         child_sets=[control_command_set, experiment_command_set])

    def test_communication(self, iterations=10):
        test_response_time(self.robot, iterations=iterations, print_response_time=True)


# === TEST RESPONSE TIME ===============================================================================================
def test_response_time(bilbo, iterations=10, print_response_time=False):
    """
    Measures the response time of the Frodo robot's test method over multiple iterations.

    Args:
        iterations (int, optional): Number of test iterations. Defaults to 10.
        print_response_time (bool, optional): Whether to print individual response times. Defaults to False.

    Logs:
        - Total number of timeouts.
        - Maximum, minimum, and average response times in milliseconds.
    """
    response_times: list[(None, float)] = [None] * iterations  # List to store response times
    timeouts = 0  # Counter for timeouts

    bilbo.core.logger.info("Testing response time")

    # Perform an initial write to check if the robot responds
    data = bilbo.test("HALLO", timeout=1)

    if data is None:
        bilbo.core.logger.warning("Initial write timed out")
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
            bilbo.core.logger.info(f"{i + 1}/{iterations} Response time: {(response_times[i] * 1000):.2f} ms")
        else:
            bilbo.core.logger.warning(f"{i + 1}/{iterations} Timeout")

        time.sleep(0.25)  # Delay before next test iteration

    # Filter out None values (timeouts) from response times
    valid_times = [response_time for response_time in response_times if response_time is not None]

    # Calculate statistics
    max_time = max(valid_times)  # Maximum response time
    min_time = min(valid_times)  # Minimum response time
    avg_time = sum(valid_times) / len(valid_times)  # Average response time

    # Log results
    bilbo.core.logger.info(f"Timeouts: {timeouts}")
    bilbo.core.logger.info(f"Max time: {max_time * 1000:.2f} ms")
    bilbo.core.logger.info(f"Min time: {min_time * 1000:.2f} ms")
    bilbo.core.logger.info(f"Average time: {avg_time * 1000:.2f} ms")

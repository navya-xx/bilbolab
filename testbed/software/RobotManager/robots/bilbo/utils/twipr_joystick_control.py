import dataclasses
import threading
import time

from extensions.cli.src.cli import CommandSet, Command, CommandArgument
from extensions.joystick.joystick_manager import JoystickManager, Joystick
from robots.bilbo.twipr import BILBO
from robots.bilbo.twipr_manager import BILBO_Manager
from robots.bilbo.utils.twipr_data import TWIPR_Control_Mode
from utils.callbacks import callback_handler, CallbackContainer
from utils.logging_utils import Logger

from robots.bilbo.twipr_definitions import *

LIMIT_TORQUE_FORWARD_DEFAULT = 1
LIMIT_TORQUE_TURN_DEFAULT = 1
LIMIT_SPEED_FORWARD_DEFAULT = 1.25
LIMIT_SPEED_TURN_DEFAULT = 5

logger = Logger('joystickcontrol')


@callback_handler
class TWIPRJoystickControlCallbacks:
    new_assignment: CallbackContainer
    assigment_removed: CallbackContainer
    new_joystick: CallbackContainer
    joystick_disconnected: CallbackContainer


@dataclasses.dataclass
class JoystickAssignment:
    joystick: Joystick
    robot: BILBO


class TWIPR_JoystickControl:
    twipr_manager: BILBO_Manager
    joystick_manager: JoystickManager
    limits: dict
    assignments: dict[str, JoystickAssignment]

    callbacks: TWIPRJoystickControlCallbacks

    _run_in_thread: bool
    _thread: threading.Thread
    _exit: bool

    # ==================================================================================================================
    def __init__(self, twipr_manager: BILBO_Manager, thread=False):
        self.twipr_manager = twipr_manager

        self.joystick_manager = JoystickManager()
        self._run_in_thread = thread

        self.twipr_manager.callbacks.robot_disconnected.register(self._robotDisconnected_callback)
        self.joystick_manager.callbacks.new_joystick.register(self._newJoystick_callback)
        self.joystick_manager.callbacks.joystick_disconnected.register(self._joystickDisconnected_callback)

        self.limits = {
            'torque': {
                'forward': LIMIT_TORQUE_FORWARD_DEFAULT,
                'turn': LIMIT_TORQUE_TURN_DEFAULT,
            },
            'speed': {
                'forward': LIMIT_SPEED_FORWARD_DEFAULT,
                'turn': LIMIT_SPEED_TURN_DEFAULT,
            }
        }

        self.assignments = {}

        self.callbacks = TWIPRJoystickControlCallbacks()

        self._exit = False

        if self._run_in_thread:
            self._thread = threading.Thread(target=self._threadFunction, daemon=True)
        else:
            self._thread = None

    # ==================================================================================================================
    def init(self):
        self.joystick_manager.init()
        self.resetLimits()

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):

        self.joystick_manager.start()
        if self._run_in_thread:
            self._thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def close(self):
        self._exit = True
        if self._run_in_thread:
            self._thread.join()

    # ------------------------------------------------------------------------------------------------------------------
    def assignJoystick(self, joystick, twipr):
        if isinstance(joystick, str):
            joystick = self.joystick_manager.getJoystickById(joystick)
            if joystick is None:
                return
        if isinstance(twipr, str):
            twipr = self.twipr_manager.getRobotById(twipr)
            if twipr is None:
                return

        self.assignments[joystick.id] = JoystickAssignment(joystick, twipr)
        joystick.setButtonCallback(button=1, event='down', function=twipr.setControlMode,
                                   parameters={'mode': TWIPR_ControlMode.TWIPR_CONTROL_MODE_BALANCING})
        joystick.setButtonCallback(button=0, event='down', function=twipr.setControlMode,
                                   parameters={'mode': TWIPR_ControlMode.TWIPR_CONTROL_MODE_OFF})
        joystick.setButtonCallback(button=2, event='down', function=twipr.setControlMode,
                                   parameters={'mode': TWIPR_ControlMode.TWIPR_CONTROL_MODE_VELOCITY})
        joystick.setButtonCallback(button=4, event='down', function=twipr.beep,
                                   parameters={'frequency': 800, 'time_ms': 500, 'repeats': 1})
        logger.info(f"Assign Joystick: {joystick.id} -> Robot: {twipr.id}")

        for callback in self.callbacks.new_assignment:
            callback(joystick, twipr)

    # ------------------------------------------------------------------------------------------------------------------
    def unassignJoystick(self, joystick):
        if isinstance(joystick, str):
            joystick = self.joystick_manager.getJoystickById(joystick)
            if joystick is None:
                return

        for key, assignment in self.assignments.items():
            if assignment.joystick == joystick:
                self.assignments.pop(key)
                logger.info(f"Unassign Joystick: {joystick.id} -> Robot: {assignment.robot.id}")
                joystick.clearAllButtonCallbacks()

                for callback in self.callbacks.assigment_removed:
                    callback(joystick, assignment.robot)
                return

    # ------------------------------------------------------------------------------------------------------------------
    def resetLimits(self):
        self.limits['torque']['forward'] = LIMIT_TORQUE_FORWARD_DEFAULT
        self.limits['torque']['turn'] = LIMIT_TORQUE_TURN_DEFAULT
        self.limits['speed']['forward'] = LIMIT_SPEED_FORWARD_DEFAULT
        self.limits['speed']['turn'] = LIMIT_SPEED_TURN_DEFAULT

    # ------------------------------------------------------------------------------------------------------------------
    def update(self):
        for assignment in self.assignments.values():
            # Check which mode the robot is in
            if assignment.robot.data.control.mode == TWIPR_Control_Mode.TWIPR_CONTROL_MODE_BALANCING:
                inputs = self._calculateNormalizedTorques(assignment)
                assignment.robot.setNormalizedBalancingInput(forward=inputs[0], turn=inputs[1])
            elif assignment.robot.data.control.mode == TWIPR_Control_Mode.TWIPR_CONTROL_MODE_VELOCITY:
                speeds = self._calculateSpeeds(assignment)
                assignment.robot.setSpeed(v=speeds[0], psi_dot=speeds[1])

    # ------------------------------------------------------------------------------------------------------------------
    def _calculateNormalizedTorques(self, assignment: JoystickAssignment) -> list:
        # Read the Joystick axes
        forward_joystick = -assignment.joystick.axis[1]
        turn_joystick = -assignment.joystick.axis[2]

        # Calculate the commands
        forward_cmd = forward_joystick
        turn_cmd = turn_joystick

        # # Calculate the torques (negative values: forward)
        # torque_left = -(forward_cmd + turn_cmd)
        # torque_right = -(forward_cmd - turn_cmd)

        return [forward_cmd, turn_cmd]

    # ------------------------------------------------------------------------------------------------------------------
    def _calculateSpeeds(self, assignment: JoystickAssignment) -> list:
        forward_joystick = -assignment.joystick.axis[1]
        turn_joystick = -assignment.joystick.axis[2]

        # Calculate the commands
        v = forward_joystick * self.limits['speed']['forward']
        psi_dot = turn_joystick * self.limits['speed']['turn']

        return [v, psi_dot]

    # ------------------------------------------------------------------------------------------------------------------
    def _threadFunction(self):
        while not self._exit:
            self.update()
            time.sleep(0.1)

    # ------------------------------------------------------------------------------------------------------------------
    def _robotDisconnected_callback(self, robot, *args, **kwargs):
        for assignment in self.assignments.values():
            if assignment.robot == robot:
                self.unassignJoystick(assignment.joystick)
                return

    # ------------------------------------------------------------------------------------------------------------------
    def _newJoystick_callback(self, joystick, *args, **kwargs):
        for callback in self.callbacks.new_joystick:
            callback(joystick)

    # ------------------------------------------------------------------------------------------------------------------
    def _joystickDisconnected_callback(self, joystick, *args, **kwargs):
        try:
            for assignment in self.assignments.values():
                if assignment.joystick == joystick:
                    self.unassignJoystick(assignment.joystick)
        except Exception as e:
            ...
        for callback in self.callbacks.joystick_disconnected:
            callback(joystick)


# ======================================================================================================================
class TWIPR_JoystickControl_CommandSet(CommandSet):
    name = 'joysticks'
    description = 'Joystick Control of BILBO robots'

    def __init__(self, joystick_control: TWIPR_JoystickControl):
        super().__init__(name=self.name)

        self.joystick_control = joystick_control

        # self.manager.registerCallback('new_robot', self._newRobot_callback)
        # self.manager.registerCallback('robot_disconnected', self._robotDisconnected_callback)

        self.addCommand(TWIPR_JoystickControl_Command_List(self.joystick_control))
        self.addCommand(TWIPR_JoystickControl_Command_Assign(self.joystick_control))
        self.addCommand(TWIPR_JoystickControl_Command_Unassign(self.joystick_control))
        # self.addCommand(TWIPR_Manager_Command_List(self.manager))
        # self.addCommand(TWIPR_Manager_Command_Stop(self.manager))
        # self.addCommand(TWIPR_Manager_Command_Mode(self.manager))

    def _newRobot_callback(self, robot, *args, **kwargs):
        ...

    def _robotDisconnected_callback(self, robot, *args, **kwargs):
        ...


# ======================================================================================================================
class TWIPR_JoystickControl_Command_List(Command):
    description = 'Lists all connected Joysticks'
    name = 'list'
    joystick_control: TWIPR_JoystickControl
    arguments = {
    }

    def __init__(self, joystick_control: TWIPR_JoystickControl):
        super().__init__(name=self.name, callback=None, description=self.description)
        self.joystick_control = joystick_control

    def function(self, *args, **kwargs):
        ...


class TWIPR_JoystickControl_Command_Assign(Command):
    description = 'Assigns a Joystick to a BILBO'
    name = 'assign'
    joystick_control: TWIPR_JoystickControl
    arguments = {
        'joystick': CommandArgument(
            name='joystick',
            type=str,
            short_name='j',
            description='ID of the Joystick to assign',
            is_flag=False,
        ),
        'robot': CommandArgument(
            name='robot',
            type=str,
            short_name='r',
            description='ID of the robot to assign',
            is_flag=False,
        )
    }

    def __init__(self, joystick_control: TWIPR_JoystickControl):
        super().__init__(name=self.name, callback=None, description=self.description)
        self.joystick_control = joystick_control

    def function(self, *args, **kwargs):
        ...


class TWIPR_JoystickControl_Command_Unassign(Command):
    description = 'Unassigns a joystick from a robot. If not arguments are given, it unassigns all.'
    name = 'unassign'
    joystick_control: TWIPR_JoystickControl
    arguments = {
        'joystick': CommandArgument(
            name='joystick',
            type=str,
            short_name='j',
            description='ID of the Joystick to unassign',
            optional=True,
            default=None,
        ),
        'robot': CommandArgument(
            name='robot',
            type=str,
            short_name='r',
            description='ID of the robot to unassign',
            optional=True,
            default=None
        )
    }

    def __init__(self, joystick_control: TWIPR_JoystickControl):
        super().__init__(name=self.name, callback=None, description=self.description)
        self.joystick_control = joystick_control

    def function(self, *args, **kwargs):
        ...

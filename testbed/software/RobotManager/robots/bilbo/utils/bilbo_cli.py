# from robots.bilbo.bilbo_manager import BILBO_Manager
# from robots.bilbo.bilbo import BILBO
from extensions.cli.src.cli import *


# BILBO Command Set
# General Commands:
# info --detail
# stop
# controlmode -m
# controlconfig --config
# statefeedback --gain
# input -l -r
# speed -f -t
# sensors --detail
# state --detail
# stream --values
# led --front --back --all --color
# restart

# ======================================================================================================================
class BILBO_CommandSet(CommandSet):

    def __init__(self, robot: 'BILBO'):
        self.robot = robot

        beep_command = Command(name='beep',
                               callback=self.robot.beep,
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

        super().__init__(name=f"{robot.id}", commands=[beep_command,
                                                       mode_command,
                                                       stop_command,
                                                       read_state_command],

                         child_sets=[control_command_set])


# ======================================================================================================================
class BILBO_Manager_CommandSet(CommandSet):
    name = 'robots'
    description = 'Functions related to connected BILBO'

    def __init__(self, bilbo_manager: 'BILBO_Manager'):
        self.bilbo_manager = bilbo_manager

        stop_command = Command(name='stop',
                               callback=self.bilbo_manager.emergencyStop,
                               description='Deactivates the control on all BILBO robots', )

        super().__init__(self.name, commands=[stop_command], child_sets=[], description=self.description)


# ======================================================================================================================
#
#
# class TWIPR_CommandSet(CommandSet):
#     robot: BILBO
#
#     def __init__(self, robot: BILBO):
#         super().__init__(name=robot.id)
#         self.robot = robot
#
#
# # BILBO Manager Command Set
#
# # stop
# # info
# # list --detail
# # controlmode -a -m --all
# # stream
#
# class TWIPR_Manager_CommandSet(CommandSet):
#     name = 'robots'
#     description = 'Functions related to connected BILBO'
#
#     def __init__(self, manager: BILBO_Manager):
#         super().__init__(name=self.name)
#
#         self.manager = manager
#
#         self.manager.registerCallback('new_robot', self._newRobot_callback)
#         self.manager.registerCallback('robot_disconnected', self._robotDisconnected_callback)
#
#         self.addCommand(TWIPR_Manager_Command_List(self.manager))
#         self.addCommand(TWIPR_Manager_Command_Stop(self.manager))
#         self.addCommand(TWIPR_Manager_Command_Mode(self.manager))
#
#     def _newRobot_callback(self, robot, *args, **kwargs):
#         ...
#
#     def _robotDisconnected_callback(self, robot, *args, **kwargs):
#         ...
#
#
# # ======================================================================================================================
# class TWIPR_Manager_Command_List(Command):
#     description = 'Lists all connected BILBO robots'
#     name = 'list'
#     manager: BILBO_Manager
#     arguments = {
#         'detail': CommandArgument(
#             name='detail',
#             type=bool,
#             short_name='d',
#             description='Shows detailed information for each robot',
#             is_flag=True,
#             default=False
#         )
#     }
#
#     def __init__(self, manager: BILBO_Manager):
#         super().__init__(name=self.name, callback=None, description=self.description)
#         self.manager = manager
#
#     def function(self, *args, **kwargs):
#         if self.manager.connected_robots == 0:
#             print("No robots connected")
#             return
#
#         for id, robot in self.manager.robots.items():
#             print(f"ID: \"{id}\" \t Rev: {robot.device.information.revision}")
#
#
# # ======================================================================================================================
# class TWIPR_Manager_Command_Stop(Command):
#     description = 'Deactivates the control on selected (or all) BILBO robots'
#     name = 'stop'
#     manager: BILBO_Manager
#     arguments = {
#         'robot': CommandArgument(
#             name='robot',
#             type=str,
#             short_name='r',
#             description='ID of the robot',
#             is_flag=False,
#             optional=True,
#             default=None
#         )
#     }
#
#     def __init__(self, manager: BILBO_Manager):
#         super().__init__(name=self.name, callback=None, description=self.description, arguments=None)
#         self.manager = manager
#
#     def function(self, robot=None, *args, **kwargs):
#
#         if robot is None:
#             for id, robot in self.manager.robots.items():
#                 robot.stop()
#             return
#
#         if robot is not None:
#             if robot in self.manager.robots:
#                 self.manager.robots[robot].stop()
#             else:
#                 logger.warning(f"Robot \"{robot}\" not found.")
#
#
# # ======================================================================================================================
# class TWIPR_Manager_Command_Mode(Command):
#     description = 'Sets the control mode of selected (or all) BILBO robots'
#     name = 'mode'
#     manager: BILBO_Manager
#     arguments = {
#         'mode': CommandArgument(
#             name='mode',
#             type=int,
#             short_name='m',
#             description='Mode of control (0:off, 1:direct, 2:torque)',
#             is_flag=False,
#             optional=False,
#             default=None
#         ),
#         'robot': CommandArgument(
#             name='robot',
#             type=str,
#             short_name='r',
#             description='ID of the robot',
#             is_flag=False,
#             optional=True,
#             default=None
#         ),
#
#     }
#
#     def __init__(self, manager: BILBO_Manager):
#         super().__init__(name=self.name, callback=None, description=self.description, arguments=None)
#         self.manager = manager
#
#     def function(self, mode: int, robot=None, *args, **kwargs):
#
#         if robot is None:
#             for id, robot in self.manager.robots.items():
#                 robot.setControlMode(mode)
#             return
#
#         if robot is not None:
#             if robot in self.manager.robots:
#                 self.manager.robots[robot].setControlMode(mode)
#             else:
#                 logger.warning(f"Robot \"{robot}\" not found.")
#
# # ======================================================================================================================

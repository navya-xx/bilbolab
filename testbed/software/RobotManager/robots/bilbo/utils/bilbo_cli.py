# from robots.bilbo.bilbo_manager import BILBO_Manager
# from robots.bilbo.bilbo import BILBO
from extensions.cli.src.cli import *
from robots.bilbo.utils.bilbo_utils import test_response_time


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
                                ],)

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
                                          callback=self.robot.experiments.runTestTrajectory,
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
                                                              optional=False,),
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


# ======================================================================================================================
class BILBO_Manager_CommandSet(CommandSet):
    name = 'robots'
    description = 'Functions related to connected BILBO'

    def __init__(self, bilbo_manager: 'BILBO_Manager'):
        self.bilbo_manager = bilbo_manager

        stop_command = Command(name='stop',
                               callback=self.bilbo_manager.emergencyStop,
                               description='Deactivates the control on all BILBO robots', )

        list_command = Command(name='list',
                               callback=self._list_robots,
                               description='', )

        super().__init__(self.name, commands=[stop_command, list_command], child_sets=[], description=self.description)

    def _list_robots(self):
        output = ""
        for robot in self.bilbo_manager.robots.values():
            output += f"{robot.id} \t {robot.device.information.revision} \n"
        return output

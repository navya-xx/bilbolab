from extensions.cli.src.cli import CommandSet, Command


# ======================================================================================================================
class BILBO_Manager_CommandSet(CommandSet):
    name = 'robots'
    description = 'Functions related to connected BILBO'

    def __init__(self, bilbo_manager: 'BILBO_Manager') -> None:

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

import threading
import time

from applications.FRODO.frodo_agent import FRODO_Agent
from applications.FRODO.tracker.tracker import Tracker
from extensions.cli.cli_gui import CLI_GUI_Server
from extensions.cli.src.cli import CommandSet
from robots.frodo.frodo import Frodo
from robots.frodo.frodo_manager import FrodoManager
from robots.frodo.utils.frodo_manager_cli import FrodoManager_Commands
from core.utils.orientation.plot_2d.dynamic.dynamic_2d_plotter import Dynamic2DPlotter
from core.utils.sound.sound import speak
from core.utils.logging_utils import Logger, setLoggerLevel

setLoggerLevel('Sound', 'INFO')

time1 = time.perf_counter()


# ======================================================================================================================
class FRODO_Application:
    agents: dict[str, FRODO_Agent]
    manager: FrodoManager
    tracker: (Tracker, None)
    cli_gui: CLI_GUI_Server

    plotter: (Dynamic2DPlotter, None)
    logger: Logger

    _exit: bool = False
    _thread: threading.Thread

    # === CONSTRUCTOR ==================================================================================================
    def __init__(self, enable_tracking: bool = True, plot_2d=True):
        self.manager = FrodoManager()
        self.manager.callbacks.new_robot.register(self._new_robot_callback)
        self.manager.callbacks.robot_disconnected.register(self._robot_disconnected_callback)

        self.agents = {}

        # if enable_tracking:
        #     self.tracker = Tracker()
        # else:
        #     self.tracker = None
        #
        # if self.tracker:
        #     self.tracker.callbacks.new_sample.register(self._tracker_new_sample)
        #     self.tracker.callbacks.description_received.register(self._tracker_description_received)
        #
        # self.cli_gui = CLI_GUI_Server(address='localhost', port=8080)
        #
        # # -- IO --
        # self.logger = Logger('APP')
        # self.logger.setLevel('INFO')
        # self.soundsystem = SoundSystem(primary_engine='etts')
        # self.soundsystem.start()
        #
        # if plot_2d:
        #     self.plotter = Dynamic2DPlotter()
        # else:
        #     self.plotter = None
        #
        # # self._thread = threading.Thread(target=self._task, daemon=True)
        #
        # self.timer = PrecisionTimer(timeout=0.1, repeat=True, callback=self.update)

        # self.exit = ExitHandler(self.close)

    # === METHODS ======================================================================================================
    def init(self):
        self.manager.init()

        # if self.tracker:
        #     self.tracker.init()
        #
        # self._getRootCLISet()

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):
        self.manager.start()
        # self.cli_gui.start()
        #
        # if self.plotter:
        #     self.plotter.start()
        #     self._prepare_plotting()
        #
        # if self.tracker:
        #     self.tracker.start()
        #
        # # self._thread.start()
        # self.timer.start()
        # speak("Start Frodo Application")

    # ------------------------------------------------------------------------------------------------------------------
    def close(self, *args, **kwargs):
        speak("Closing Frodo Application")
        self._exit = True
        time.sleep(2)

    # === METHODS ======================================================================================================
    def update(self):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def _getRootCLISet(self):

        command_set_robots = FrodoManager_Commands(self.manager)

        command_set_optitrack = CommandSet('optitrack',
                                           commands=[])

        command_set_joysticks = CommandSet('joysticks',
                                           commands=[])

        command_set_experiments = CommandSet('experiments',
                                             commands=[])

        command_set_root = CommandSet('.',
                                      child_sets=[command_set_robots,
                                                  command_set_optitrack,
                                                  command_set_joysticks,
                                                  command_set_experiments])

        self.cli_gui.updateCLI(command_set_root)

    # ------------------------------------------------------------------------------------------------------------------
    def _robot_disconnected_callback(self, robot):
        speak(f'Robot {robot.id} disconnected')
        self.cli_gui.sendLog(f'Robot {robot.id} disconnected')

        if robot.id in self.cli_gui.cli.root_set.child_sets['robots'].child_sets:
            self.cli_gui.cli.root_set.child_sets['robots'].removeChild(robot.id)
            self.cli_gui.updateCLI()

        # Remove the agent
        if robot.id in self.agents:
            del self.agents[robot.id]
            self.plotter.remove_element_by_id(f'agents/{robot.id}')

    # ------------------------------------------------------------------------------------------------------------------
    def _new_robot_callback(self, robot: Frodo):
        speak(f"New Robot {robot.id} connected")
        # self.cli_gui.sendLog(f'New Robot {robot.id} connected')

        # Add a new agent
        agent = FRODO_Agent(id=robot.id, robot=robot)
        self.agents[robot.id] = agent


# ======================================================================================================================
def start_frodo_application():
    app = FRODO_Application(enable_tracking=False, plot_2d=True)
    app.init()
    app.start()

    while True:
        time.sleep(2)


# ======================================================================================================================
if __name__ == '__main__':
    start_frodo_application()

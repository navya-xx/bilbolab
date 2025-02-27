import logging
import time

from extensions.cli.cli_gui import CLI_GUI_Server
from extensions.cli.src.cli import CLI, CommandSet, Command
from robots.bilbo.bilbo_manager import BILBO_Manager
from utils.exit import ExitHandler
from utils.logging_utils import setLoggerLevel, Logger
from utils.loop import infinite_loop
from utils.sound.sound import speak, SoundSystem

# ======================================================================================================================
ENABLE_SPEECH_OUTPUT = True


# ======================================================================================================================
class BILBO_Application:
    robot_manager: BILBO_Manager

    def __init__(self):
        self.robot_manager = BILBO_Manager(robot_auto_start=False)

        # self.robot_manager.callbacks.stream.register(self.gui.sendRawStream)
        self.robot_manager.callbacks.new_robot.register(self._newRobot_callback)
        self.robot_manager.callbacks.robot_disconnected.register(self._robotDisconnected_callback)

        # CLI
        self.cli_server = CLI_GUI_Server(address='localhost', port=8090)
        self.cli_server.cli.setRootSet(CommandSet('.'))

        # Logging
        self.logger = Logger('APP')
        self.logger.setLevel('INFO')

        # Sound System for speaking and sounds
        self.soundsystem = SoundSystem(primary_engine='etts')
        self.soundsystem.start()

        # Exit Handling
        self.exit = ExitHandler()
        self.exit.register(self.close)

    # ------------------------------------------------------------------------------------------------------------------
    def init(self):
        setLoggerLevel(logger=['tcp', 'server', 'UDP', 'UDP Socket', 'Sound'], level=logging.WARNING)

        self.robot_manager.init()
        self.cli_server.cli.getByPath('.').addChild(self.robot_manager.cli_command_set)

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):
        self.cli_server.start()
        self.logger.info('Starting Bilbo application')
        speak('Start Bilbo application')
        self.robot_manager.start()

    # ------------------------------------------------------------------------------------------------------------------
    def close(self, *args, **kwargs):
        speak('Stop Bilbo application')
        self.logger.info('Closing Bilbo application')
        time.sleep(2)
        global ENABLE_SPEECH_OUTPUT
        ENABLE_SPEECH_OUTPUT = False

    # ==================================================================================================================

    # ------------------------------------------------------------------------------------------------------------------
    # ==================================================================================================================
    def _newRobot_callback(self, bilbo, *args, **kwargs):
        if ENABLE_SPEECH_OUTPUT:
            speak(f"Robot {bilbo.id} connected")

        # self.logger.info(f"Robot connected: {bilbo.id}")

    # ------------------------------------------------------------------------------------------------------------------
    def _robotDisconnected_callback(self, bilbo, *args, **kwargs):
        if ENABLE_SPEECH_OUTPUT:
            speak(f"Robot {bilbo.id} disconnected")

        # self.logger.info(f"Robot disconnected: {bilbo.id}")


# ======================================================================================================================
def run_bilbo_application():
    app = BILBO_Application()
    app.init()
    app.start()

    infinite_loop()


if __name__ == '__main__':
    run_bilbo_application()

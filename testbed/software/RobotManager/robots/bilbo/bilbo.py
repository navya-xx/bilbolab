from time import sleep

from matplotlib import pyplot as plt

from core.device import Device
from robots.bilbo.utils.bilbo_cli import BILBO_CommandSet
from robots.bilbo.utils.bilbo_utils import BILBO_Assets
from robots.bilbo.utils.twipr_data import TWIPR_Data, twiprSampleFromDict
from utils.data import generate_time_vector, generate_random_input
from utils.events import EventListener, event_handler, ConditionEvent
from utils.logging_utils import Logger, LOG_LEVELS
from robots.bilbo.bilbo_definitions import *
from utils.sound.sound import speak, playSound


# ======================================================================================================================
class BILBO_Control:
    ...

    def __init__(self, id, device: Device, logger: Logger):
        self.id = id
        self.device = device
        self.logger = logger

    # ------------------------------------------------------------------------------------------------------------------
    def setControlMode(self, mode: (int, BILBO_Control_Mode), *args, **kwargs):
        if isinstance(mode, int):
            mode = BILBO_Control_Mode(mode)

        self.logger.info(f"Robot {self.id}: Set Control Mode to {mode.name}")
        self.device.function(function='setControlMode', data={'mode': mode})

    # ------------------------------------------------------------------------------------------------------------------
    def getControlState(self):
        ...

    def setStateFeedbackGain(self, gain: float):
        ...

    def setForwardPID(self, p, i, d):
        ...

    def setTurnPID(self, p, i, d):
        ...

    def readControlConfiguration(self):
        ...


# ======================================================================================================================
@event_handler
class BILBO_Experiments_Events:
    finished: ConditionEvent = ConditionEvent(flags=[('trajectory_id', int)])
    aborted: ConditionEvent = ConditionEvent(flags=[('trajectory_id', int)])

class BILBO_Experiments:

    def __init__(self, id, logger: Logger, device: Device, assets: BILBO_Assets):
        self.id = id
        self.logger = logger
        self.device = device
        self.assets = assets

        self.events = BILBO_Experiments_Events()
        self.device.events.event.on(self._trajectory_event_callback, flags={'type': 'trajectory'})

    def runTestTrajectory(self, num, time, frequency=2, gain=0.25):
        t_vector = generate_time_vector(start=0, end=time, dt=BILBO_CONTROL_DT)

        if len(t_vector) > MAX_STEPS_TRAJECTORY:
            self.logger.warning("Trajectory too long")
            return None

        input = generate_random_input(t_vector=t_vector, f_cutoff=frequency, sigma_I=gain)
        outputs = []

        speak(f"{self.id}: Test Trajectory Program with {num} trajectories")

        for i in range(num):
            trajectory_id = i+1

            if self.assets.joystick:
                self.assets.joystick.events.button.wait(timeout=None, flags={'button': 'R1'})
                playSound('notification')
                speak(f"{self.id}: Start trajectory {trajectory_id} of {num}")

            self.logger.info(f"Running test trajectory {trajectory_id}")
            self.device.function(
                function='runTrajectory',
                data={
                    'trajectory_id': trajectory_id,
                    'input': [[float(inp), float(inp)] for inp in input],
                    'signals': ['lowlevel.estimation.state.theta']
                },
                request_response=False,
            )

            success = self.events.finished.wait(flags={'trajectory_id': trajectory_id},
                                                timeout=time+2)

            if success:
                self.logger.info(f"Trajectory {trajectory_id} finished successfully")
                data = self.events.finished.get_data()
                outputs.append(data['output']['lowlevel.estimation.state.theta'])

                if self.assets.joystick:
                    self.assets.joystick.rumble(duration=200, strength=0.5)

            else:
                self.logger.error(f"Trajectory {trajectory_id} failed")
                break

            sleep(1)

        speak(f"{self.id}: Test Trajectory Program finished")
        for i in range(num):
            plt.plot(t_vector, outputs[i])

        plt.grid()
        plt.show()

    def startTrajectory(self):
        ...

    def sendTrajectory(self):
        ...

    def stopTrajectory(self):
        ...

    def _trajectory_event_callback(self, message, *args, **kwargs):
        if not 'event' in message.data:
            self.logger.error(f"Robot {self.id}: Received trajectory event without event field")

        if message.data['event'] == 'finished':
            self.logger.info(f"Trajectory {message.data['trajectory_id']} finished. Len: {len(message.data['input'])}")
            speak(f"{self.id}: Trajectory {message.data['trajectory_id']} finished")

            self.events.finished.set(resource=message.data, flags={'trajectory_id': message.data['trajectory_id']})


# ======================================================================================================================
class BILBO:
    device: Device
    control: BILBO_Control
    experiments: BILBO_Experiments
    assets: BILBO_Assets

    callbacks: dict
    data: TWIPR_Data
    logger: Logger

    def __init__(self, device: Device, *args, **kwargs):
        self.device = device

        self.callbacks = {
            'stream': []
        }

        self.logger = Logger(f"{self.id}")
        self.logger.setLevel('DEBUG')

        self.assets = BILBO_Assets()
        self.control = BILBO_Control(self.id, device, self.logger)
        self.experiments = BILBO_Experiments(self.id, self.logger, device, assets=self.assets)


        self.data = TWIPR_Data()
        self.cli_command_set = BILBO_CommandSet(self)

        self.device.callbacks.stream.register(self._onStreamCallback)
        self.device.callbacks.disconnected.register(self._disconnected_callback)
        self.device.callbacks.event.register(self.gotEvent)

    # ------------------------------------------------------------------------------------------------------------------
    def gotEvent(self, message, *args, **kwargs):
        # self.logger.info(f"Got Event {self.id}: {message}")
        if message.event == 'log':
            self._handleLog(message.data)

    # ------------------------------------------------------------------------------------------------------------------
    def setControlConfiguration(self, config):
        raise NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    def loadControlConfiguration(self, name):
        raise NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    def saveControlConfiguration(self, name):
        raise NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    def setNormalizedBalancingInput(self, forward, turn, *args, **kwargs):
        self.device.function('setNormalizedBalancingInput', data={'forward': forward, 'turn': turn})

    # ------------------------------------------------------------------------------------------------------------------
    def setSpeed(self, v, psi_dot, *args, **kwargs):
        self.device.function('setSpeed', data={'v': v, 'psi_dot': psi_dot})

    # ------------------------------------------------------------------------------------------------------------------
    def setBalancingInput(self, torque, *args, **kwargs):
        self.device.function('setBalancingInput', data={'input': torque})

    # ------------------------------------------------------------------------------------------------------------------
    def setDirectInput(self, left, right, *args, **kwargs):
        self.device.function('setDirectInput', data={'left': left, 'right': right})

    # ------------------------------------------------------------------------------------------------------------------
    def test(self, input, timeout=1):
        try:
            data = self.device.function(function='test',
                                        data={'input': input},
                                        return_type=dict,
                                        request_response=True,
                                        timeout=timeout)
        except TimeoutError:
            data = None
        return data

    # === CLASS METHODS =====================================================================

    # === METHODS ============================================================================

    # === PROPERTIES ============================================================================
    @property
    def id(self):
        return self.device.information.device_id

    # === COMMANDS ===========================================================================
    def balance(self, state):
        self.control.setControlMode(BILBO_Control_Mode.BALANCING)

    # ------------------------------------------------------------------------------------------------------------------
    def beep(self, frequency, time_ms, repeats):
        self.device.function(function='beep', data={'frequency': 250, 'time_ms': 250, 'repeats': 1})

    # ------------------------------------------------------------------------------------------------------------------
    def speak(self, text):
        self.device.function(function='speak', data={'message': text})

    # ------------------------------------------------------------------------------------------------------------------
    def stop(self):
        self.control.setControlMode(0)

    # ------------------------------------------------------------------------------------------------------------------
    def setLEDs(self, red, green, blue):
        self.device.function('setLEDs', data={'red': red, 'green': green, 'blue': blue})

    # ------------------------------------------------------------------------------------------------------------------
    def _onStreamCallback(self, stream, *args, **kwargs):
        self.data = twiprSampleFromDict(stream.data)

    # ------------------------------------------------------------------------------------------------------------------
    def _handleLog(self, log_data):
        if log_data['level'] == LOG_LEVELS['ERROR']:
            self.logger.error(f"({log_data['logger']}): {log_data['message']}")
        elif log_data['level'] == LOG_LEVELS['WARNING']:
            self.logger.warning(f"({log_data['logger']}): {log_data['message']}")
        elif log_data['level'] == LOG_LEVELS['INFO']:
            self.logger.info(f"({log_data['logger']}): {log_data['message']}")
        elif log_data['level'] == LOG_LEVELS['DEBUG']:
            self.logger.debug(f"({log_data['logger']}): {log_data['message']}")

    # ------------------------------------------------------------------------------------------------------------------
    def _disconnected_callback(self, *args, **kwargs):
        del self.experiments

    def __del__(self):
        print(f"Deleting {self.id}")

from core.device import Device
from robots.bilbo.utils.bilbo_cli import BILBO_CommandSet
from robots.bilbo.utils.twipr_data import TWIPR_Data, twiprSampleFromDict
from utils.logging_utils import Logger

from robots.bilbo.bilbo_definitions import *


# ======================================================================================================================
class BILBO_Control:
    ...

    def __init__(self, id, device: Device, logger: Logger):
        self.id = id
        self.device = device
        self.logger = logger

    # ------------------------------------------------------------------------------------------------------------------
    def setControlMode(self, mode: (int, TWIPR_ControlMode)):
        if isinstance(mode, int):
            mode = TWIPR_ControlMode(mode)

        self.logger.debug(f"Robot {self.id}: Set Control Mode to {mode}")
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
class BILBO:
    device: Device
    control: BILBO_Control
    callbacks: dict
    data: TWIPR_Data
    logger: Logger

    def __init__(self, device: Device, *args, **kwargs):
        self.device = device

        self.callbacks = {
            'stream': []
        }

        self.logger = Logger(f"{self.id}")
        self.control = BILBO_Control(self.id, device, self.logger)

        self.data = TWIPR_Data()
        self.device.callbacks.stream.register(self._onStreamCallback)

        self.cli_command_set = BILBO_CommandSet(self)

        self.device.callbacks.event.register(self.gotEvent)

    def gotEvent(self, message, *args, **kwargs):
        self.logger.info(f"Got Event {self.id}: {message}")

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

    # === CLASS METHODS =====================================================================

    # === METHODS ============================================================================

    # === PROPERTIES ============================================================================
    @property
    def id(self):
        return self.device.information.device_id

    # === COMMANDS ===========================================================================
    def balance(self, state):
        self.control.setControlMode(TWIPR_ControlMode.TWIPR_CONTROL_MODE_BALANCING)

    # ------------------------------------------------------------------------------------------------------------------
    def beep(self, frequency, time_ms, repeats):
        self.device.function(function='beep', data={'frequency': 250, 'time_ms': 250, 'repeats': 1})

    # ------------------------------------------------------------------------------------------------------------------
    def stop(self):
        self.control.setControlMode(0)

    # ------------------------------------------------------------------------------------------------------------------
    def setLEDs(self, red, green, blue):
        ...
        self.device.function('setLEDs', data={'red': red, 'green': green, 'blue': blue})

    # ------------------------------------------------------------------------------------------------------------------
    def setTestParameter(self, value):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def _onStreamCallback(self, stream, *args, **kwargs):
        self.data = twiprSampleFromDict(stream.data)

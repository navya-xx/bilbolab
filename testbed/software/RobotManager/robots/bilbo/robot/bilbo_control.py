from robots.bilbo.robot.bilbo_core import BILBO_Core
from robots.bilbo.robot.bilbo_definitions import BILBO_Control_Mode
from core.utils.events import event_definition, ConditionEvent


@event_definition
class BILBO_Control_Events:
    mode_changed: ConditionEvent = ConditionEvent(flags=[('mode', BILBO_Control_Mode)])
    configuration_changed: ConditionEvent
    error: ConditionEvent


# ======================================================================================================================
class BILBO_Control:

    def __init__(self, core: BILBO_Core):
        self.id = core.id
        self.device = core.device
        self.logger = core.logger

        self.core = core

        self.events = BILBO_Control_Events()

        self.device.events.event.on(callback=self.handleEventMessage, flags={'event': 'control'})

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

    def enableTIC(self, state):
        self.device.function(function='enableTIC', data={
            'enable': state
        })

    def handleEventMessage(self, message):
        ...

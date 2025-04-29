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
    mode: (BILBO_Control_Mode, None)

    # === INIT =========================================================================================================
    def __init__(self, core: BILBO_Core):
        self.id = core.id
        self.device = core.device
        self.logger = core.logger

        self.core = core
        self.events = BILBO_Control_Events()

        self.mode = None

        self.device.events.event.on(callback=self.handleEventMessage, flags={'event': 'control'}, input_resource=True)
        self.device.events.stream.on(callback=self._handle_stream, input_resource=True)

    # ------------------------------------------------------------------------------------------------------------------
    def setControlMode(self, mode: (int, BILBO_Control_Mode), *args, **kwargs):
        if isinstance(mode, int):
            mode = BILBO_Control_Mode(mode)

        self.logger.info(f"Robot {self.id}: Set Control Mode to {mode.name}")
        self.device.function(function='setControlMode', data={'mode': mode})

    # ------------------------------------------------------------------------------------------------------------------
    def setNormalizedBalancingInput(self, forward, turn, *args, **kwargs):
        self.device.function('setNormalizedBalancingInput', data={'forward': forward, 'turn': turn})

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

    def setWaypoints(self, waypoints):
        self.device.function(function='setWaypoints', data={
            'waypoints': waypoints
        })

    def handleEventMessage(self, message):

        match message.data['event']:
            case 'mode_change':
                ...
            case 'configuration_change':
                ...
            case 'error':
                ...
            case _:
                self.core.logger.warning(f"Unknown control event message: {message.data['event']}")

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_stream(self, stream_message):
        ...
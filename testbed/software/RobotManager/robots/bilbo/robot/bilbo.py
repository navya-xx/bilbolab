from core.device import Device
from robots.bilbo.robot.bilbo_control import BILBO_Control
from robots.bilbo.robot.bilbo_core import BILBO_Core
from robots.bilbo.robot.bilbo_experiment import BILBO_Experiments
from robots.bilbo.robot.bilbo_interfaces import BILBO_CLI_CommandSet as BILBO_CommandSet
from robots.bilbo.robot.bilbo_interfaces import BILBO_Interfaces
from robots.bilbo.robot.bilbo_data import TWIPR_Data, twiprSampleFromDict
from robots.bilbo.robot.bilbo_definitions import *


# ======================================================================================================================
class BILBO:
    device: Device
    core: BILBO_Core
    control: BILBO_Control
    experiments: BILBO_Experiments

    interfaces: BILBO_Interfaces

    data: TWIPR_Data

    # ==================================================================================================================
    def __init__(self, device: Device, *args, **kwargs):
        self.device = device

        self.core = BILBO_Core(device=device, robot_id=self.device.information.device_id)

        self.control = BILBO_Control(core=self.core)
        self.experiments = BILBO_Experiments(core=self.core)
        self.interfaces = BILBO_Interfaces(core=self.core, control=self.control)

        self.data = TWIPR_Data()



        # TODO Remove this from here
        self.cli_command_set = BILBO_CommandSet(self)

        self.device.callbacks.stream.register(self._onStreamCallback)
        self.device.callbacks.disconnected.register(self._disconnected_callback)

        self.interfaces.openLivePlot('theta')

    # ------------------------------------------------------------------------------------------------------------------
    def setControlConfiguration(self, config):
        raise NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    def loadControlConfiguration(self, name):
        raise NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    def saveControlConfiguration(self, name):
        raise NotImplementedError

    #
    #
    # # ------------------------------------------------------------------------------------------------------------------
    # def setSpeed(self, v, psi_dot, *args, **kwargs):
    #     self.device.function('setSpeed', data={'v': v, 'psi_dot': psi_dot})
    #
    # # ------------------------------------------------------------------------------------------------------------------
    # def setBalancingInput(self, torque, *args, **kwargs):
    #     self.device.function('setBalancingInput', data={'input': torque})
    #
    # # ------------------------------------------------------------------------------------------------------------------
    # def setDirectInput(self, left, right, *args, **kwargs):
    #     self.device.function('setDirectInput', data={'left': left, 'right': right})

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
    def _disconnected_callback(self, *args, **kwargs):
        del self.experiments

    # ------------------------------------------------------------------------------------------------------------------
    def __del__(self):
        print(f"Deleting {self.id}")

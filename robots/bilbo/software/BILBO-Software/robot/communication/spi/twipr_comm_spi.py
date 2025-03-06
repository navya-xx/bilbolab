import time
from ctypes import sizeof

# === OWN PACKAGES =====================================================================================================
from core.communication.spi.spi import SPI_Interface
from utils.callbacks import callback_handler, CallbackContainer
from utils.dataclass_utils import from_dict
# from utils.exit import ExitHandler
from robot.lowlevel.stm32_sample import bilbo_ll_sample_struct, BILBO_LL_Sample
from utils.ctypes_utils import bytes_to_value
from robot.lowlevel.stm32_sample import SAMPLE_BUFFER_LL_SIZE
from control_board.hardware.hardware import GPIO_Input, InterruptFlank, PullupPulldown
from utils.time import performance_analyzer


# ======================================================================================================================
@callback_handler
class BILBO_SPI_Callbacks:
    rx_latest_sample: CallbackContainer
    rx_samples: CallbackContainer


# ======================================================================================================================
class BILBO_SPI_Interface:
    interface: SPI_Interface
    callbacks: BILBO_SPI_Callbacks
    sample_notification_pin: int

    gpio_input: (None, GPIO_Input)

    def __init__(self, interface: SPI_Interface, sample_notification_pin):
        self.interface = interface
        self.sample_notification_pin = sample_notification_pin
        self.callbacks = BILBO_SPI_Callbacks()

        self.gpio_input = None
        # self.exit = ExitHandler()
        # self.exit.register(self.close)

    # === METHODS ======================================================================================================
    def init(self):
        self._configureSampleGPIO()
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def close(self, *args, **kwargs):
        ...

    def send(self, data: (bytes, bytearray)):
        self.interface.send(data)

    # === PRIVATE METHODS ==============================================================================================
    def _configureSampleGPIO(self):
        time.sleep(0.25)
        self.gpio_input = GPIO_Input(
            pin=self.sample_notification_pin,
            pin_type='internal',
            interrupt_flank=InterruptFlank.BOTH,
            pull_up_down=PullupPulldown.DOWN,
            callback=self._samplesReadyInterrupt,
            bouncetime=1
        )

        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self.sample_notification_pin, GPIO.IN,
        #            pull_up_down=GPIO.PUD_DOWN)
        # GPIO.add_event_detect(self.sample_notification_pin, GPIO.BOTH,
        #                       callback=self._samplesReadyInterrupt, bouncetime=1)

    # ------------------------------------------------------------------------------------------------------------------
    def _samplesReadyInterrupt(self, *args, **kwargs):
        samples, latest_sample = self._readSamples()

        for callback in self.callbacks.rx_samples:
            callback(samples)

        for callback in self.callbacks.rx_latest_sample:
            callback(latest_sample)



    # ------------------------------------------------------------------------------------------------------------------
    def _readSamples(self) -> (list[dict], BILBO_LL_Sample):
        data_rx_bytes = bytearray(SAMPLE_BUFFER_LL_SIZE * sizeof(bilbo_ll_sample_struct))
        self.interface.readinto(data_rx_bytes, start=0,
                                end=SAMPLE_BUFFER_LL_SIZE * sizeof(bilbo_ll_sample_struct))
        samples = []
        for i in range(0, SAMPLE_BUFFER_LL_SIZE):
            sample = bytes_to_value(
                byte_data=data_rx_bytes[i * sizeof(bilbo_ll_sample_struct):(i + 1) * sizeof(bilbo_ll_sample_struct)],
                ctype_type=bilbo_ll_sample_struct)

            samples.append(sample)

        latest_sample = from_dict(BILBO_LL_Sample, samples[-1])
        return samples, latest_sample

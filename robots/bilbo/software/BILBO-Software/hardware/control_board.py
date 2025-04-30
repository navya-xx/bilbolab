import time

from core.utils.exit import register_exit_callback
# === OWN PACKAGES =====================================================================================================
from hardware.hardware.gpio import GPIO_Output
from core.communication.i2c.i2c import I2C_Interface
from core.communication.spi.spi import SPI_Interface
from core.communication.wifi.wifi_interface import WIFI_Interface
from core.communication.wifi.data_link import Command, CommandArgument
from core.utils.debug import debug_print
# from core.hardware.sx1508 import SX1508, SX1508_GPIO_MODE
from core.communication.serial.serial_interface import Serial_Interface
from hardware.board_config import getBoardConfig
from hardware.io_extension.io_extension import RobotControl_IO_Extension
from core.utils.logging_utils import Logger
from hardware.lowlevel_definitions import bilbo_external_rgb_struct, BILBO_AddressTables, BILBO_GeneralAddresses, \
    twipr_beep_struct

import core.hardware.eeprom as eeprom
from hardware.shields.shields import SHIELDS, SHIELD_ID_ADDRESS

# === GLOBAL VARIABLES =================================================================================================
logger = Logger("BOARD")


# === RobotControl_Board ===============================================================================================
class RobotControl_Board:
    wifi_interface: WIFI_Interface
    spi_interface: SPI_Interface
    serial_interface: Serial_Interface
    i2c_interface: I2C_Interface

    status_led: GPIO_Output
    uart_reset_pin: GPIO_Output

    io_extension: RobotControl_IO_Extension

    shield = None

    # === INIT =========================================================================================================
    def __init__(self, device_class: str = 'board', device_type: str = 'RobotControl', device_revision: str = 'v3',
                 device_id: str = 0, device_name: str = 'c4'):

        self.board_config = getBoardConfig()

        self.wifi_interface = WIFI_Interface('wifi', device_class=device_class, device_type=device_type,
                                             device_revision=device_revision, device_id=device_id,
                                             device_name=device_name)

        self.spi_interface = SPI_Interface(notification_pin=None, baudrate=10000000)

        self.serial_interface = Serial_Interface(port=self.board_config['communication']['RC_PARAMS_BOARD_STM32_UART'],
                                                 baudrate=self.board_config['communication'][
                                                     'RC_PARAMS_BOARD_STM32_UART_BAUD'])

        self.i2c_interface = I2C_Interface()

        self.io_extension = RobotControl_IO_Extension(interface=self.i2c_interface)

        # TODO: This should be defined somewhere else
        self.wifi_interface.addCommands(Command(identifier='print',
                                                callback=debug_print,
                                                arguments=['text'],
                                                description='Prints any given text'))

        self.wifi_interface.addCommand(identifier='rgbled', callback=self.io_extension.rgb_led_intern[0].setColor,
                                       arguments=['red', 'green', 'blue'], description='')

        self.wifi_interface.addCommand(identifier='beep',
                                       callback=self.beep,
                                       description='',
                                       arguments=[
                                           CommandArgument(name='frequency',
                                                           type=str,
                                                           optional=True,
                                                           default='medium',
                                                           description='Frequency of the beep. Can be "low", "medium", "high" or a number in Hz'),
                                           CommandArgument(name='time_ms',
                                                           type=int,
                                                           optional=True,
                                                           default=500,
                                                           description='Duration of the beep in ms'),
                                           CommandArgument(name='repeats',
                                                           type=int,
                                                           optional=True,
                                                           default=1,
                                                           description='Number of repeats')
                                       ])

        # This too

        self.status_led = GPIO_Output(pin_type=self.board_config['pins']['status_led']['type'],
                                      pin=self.board_config['pins']['status_led']['pin'],
                                      )

        self.setStatusLed(0)

        self.uart_reset_pin = GPIO_Output(
            pin_type=self.board_config['pins']['uart_reset']['type'],
            pin=self.board_config['pins']['uart_reset']['pin'],
            value=0,
        )

        self.wifi_interface.callbacks.connected.register(self.setStatusLed, inputs={'state': True},
                                                         discard_inputs=True)
        self.wifi_interface.callbacks.disconnected.register(self.setStatusLed, inputs={'state': False},
                                                            discard_inputs=True)

        register_exit_callback(self.handle_exit)

    # === METHODS ======================================================================================================
    def init(self):
        logger.debug("Reset UART")
        self.resetUart()
        self.shield = self.checkForShield()

    # ------------------------------------------------------------------------------------------------------------------
    def checkForShield(self):
        try:
            shield_id = eeprom.read_bytes(eeprom_address=self.board_config['devices']['SHIELD_EEPROM_I2C_ADDRESS'],
                                          byte_address=SHIELD_ID_ADDRESS,
                                          num_bytes=1)
        except Exception as e:
            return None

        # Check if the shield id is in the list of known shields
        if shield_id in SHIELDS:
            logger.info(f"Found shield: {SHIELDS[shield_id]['name']}")
            shield = SHIELDS[shield_id]['class']()
            return shield

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):
        self.wifi_interface.start()
        self.serial_interface.start()

    # ------------------------------------------------------------------------------------------------------------------
    def resetUart(self):
        self.uart_reset_pin.write(1)
        time.sleep(0.001)
        self.uart_reset_pin.write(0)

    # ------------------------------------------------------------------------------------------------------------------
    def setStatusLed(self, state, *args, **kwargs):
        self.status_led.write(state)

    # ------------------------------------------------------------------------------------------------------------------
    def setRGBLEDIntern(self, position, color):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def setRGBLEDExtern(self, color):
        color_struct = bilbo_external_rgb_struct(red=color[0], green=color[1], blue=color[2])
        self.serial_interface.function(address=BILBO_GeneralAddresses.ADDRESS_FIRMWARE_EXTERNAL_LED,
                                       module=BILBO_AddressTables.REGISTER_TABLE_GENERAL,
                                       input_type=bilbo_external_rgb_struct,
                                       data=color_struct)

    # ------------------------------------------------------------------------------------------------------------------
    def beep(self, frequency: (str, float) = None, time_ms: int = 500, repeats: int = 1):
        if frequency is None:
            frequency = 500

        if isinstance(frequency, str):
            if frequency == 'low':
                frequency = 200
            elif frequency == 'medium':
                frequency = 600
            elif frequency == 'high':
                frequency = 900
            else:
                frequency = 500

        beep_data = {
            'frequency': frequency,
            'time': time_ms,
            'repeats': repeats
        }

        self.serial_interface.function(
            address=BILBO_GeneralAddresses.ADDRESS_FIRMWARE_BEEP,
            module=0x01,
            data=beep_data,
            input_type=twipr_beep_struct
        )

    # ------------------------------------------------------------------------------------------------------------------
    def handle_exit(self, *args, **kwargs):
        self.wifi_interface.close()
        time.sleep(0.25)
        self.setStatusLed(0)
        self.setRGBLEDExtern([2, 2, 2])
        logger.info("Exit Board")

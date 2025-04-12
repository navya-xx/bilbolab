import ctypes
import enum

from core.utils.ctypes_utils import STRUCTURE


class BILBO_AddressTables(enum.IntEnum):
    REGISTER_TABLE_GENERAL = 0x01

class BILBO_GeneralAddresses(enum.IntEnum):
    ADDRESS_FIRMWARE_STATE = 0x01
    ADDRESS_FIRMWARE_TICK = 0x02
    ADDRESS_FIRMWARE_REVISION = 0x03
    ADDRESS_FIRMWARE_DEBUG = 0x04
    ADDRESS_FIRMWARE_BEEP = 0x05
    ADDRESS_BOARD_REVISION = 0x06
    ADDRESS_FIRMWARE_EXTERNAL_LED = 0x07

@STRUCTURE
class bilbo_external_rgb_struct:
    FIELDS = {
        'red': ctypes.c_uint8,
        'green': ctypes.c_uint8,
        'blue': ctypes.c_uint8,
    }


@STRUCTURE
class twipr_beep_struct:
    FIELDS = {
        'frequency': ctypes.c_float,
        'time': ctypes.c_uint16,
        'repeats': ctypes.c_uint8
    }
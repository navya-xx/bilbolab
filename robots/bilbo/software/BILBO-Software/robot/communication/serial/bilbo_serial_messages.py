from core.communication.serial.core.serial_protocol import UART_Message
from core.communication.serial.serial_interface import Serial_Interface, SerialMessage
import robot.lowlevel.stm32_addresses as addresses
from robot.lowlevel.stm32_general import twipr_firmware_revision
from robot.lowlevel.stm32_messages import *
from utils.callbacks import callback_handler, CallbackContainer
from utils.ctypes_utils import CType
from utils.events import ConditionEvent
from utils.logging_utils import Logger

class bilbo_debug_message_data_type(ctypes.Structure):
    _fields_ = [
        ("flag", ctypes.c_uint8),
        ("text", ctypes.c_char * 100)
    ]


def debugprint(data: bilbo_debug_message_data_type, *args, **kwargs):
    logger = Logger("BILBO DEBUG")
    try:
        flag = data['flag']
        text = data['text'].decode("utf-8")
        if flag == 0:
            logger.info(f"DEBUG: {text}")
        if flag == 1:
            logger.info(f"{text}")
        if flag == 2:
            logger.warning(f"{text}")
        if flag == 3:
            logger.error(f"{text}")
    except Exception as e:
        ...


class BILBO_Debug_Message(SerialMessage):
    module: int = 1
    address: int = 0xDD
    command: SerialCommandType = SerialCommandType.UART_CMD_EVENT
    data_type: type = bilbo_debug_message_data_type
    callback = staticmethod(debugprint)


BILBO_SERIAL_MESSAGES = [BILBO_Debug_Message]
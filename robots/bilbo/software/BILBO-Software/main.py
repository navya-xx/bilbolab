import ctypes
import time

from robot.bilbo import BILBO
from robot.control.definitions import BILBO_Control_Mode
from utils.static_variable import StaticVariable
from utils.events import EventListener
from utils.callbacks import Callback
from utils.logging_utils import setLoggerLevel

setLoggerLevel('wifi', 'ERROR')


def main():
    bilbo = BILBO()
    bilbo.init()
    bilbo.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()

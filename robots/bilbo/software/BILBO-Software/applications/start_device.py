import time
from robot.control.bilbo_control import BILBO_Control_Mode
from robot.bilbo import BILBO


def main():
    twipr = BILBO(reset_stm32=False)
    twipr.init()
    twipr.start()


if __name__ == '__main__':
    main()

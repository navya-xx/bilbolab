import os
import sys
import time

top_level_module = os.path.expanduser("~/robot/software")
if top_level_module not in sys.path:
    sys.path.insert(0, top_level_module)

from robot.applications.standalone.joystick_control import StandaloneJoystickControl
from robot.bilbo import BILBO


def run_standalone():
    bilbo = BILBO(reset_stm32=False)
    joystick_control = StandaloneJoystickControl(bilbo=bilbo)
    bilbo.init()
    joystick_control.init()
    bilbo.start()
    joystick_control.start()



if __name__ == '__main__':
    run_standalone()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        exit(1)

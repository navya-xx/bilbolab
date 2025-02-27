import time

from applications.BILBO.general.JoystickControl import SimpleTwiprJoystickControl
from utils.logging_utils import Logger

logger = Logger('app')
logger.setLevel('INFO')


def main():
    app = SimpleTwiprJoystickControl()
    app.init()
    app.start()

    while True:
        logger.info("Hello World")
        time.sleep(1)


if __name__ == '__main__':
    main()

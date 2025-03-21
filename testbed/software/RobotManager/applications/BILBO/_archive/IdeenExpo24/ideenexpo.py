import time

from applications.BILBO._archive.IdeenExpo24.src.ideenexpo_manager import IdeenExpoManager
from utils.logging_utils import Logger

logger = Logger('IdeenExpo')


def main():
    logger.info("Starting IdeenExpo")
    manager = IdeenExpoManager()
    manager.init()
    manager.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()

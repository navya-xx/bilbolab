import time

from utils.logging_utils import Logger
from utils.network.hosted_network import hostNetwork
from applications.BILBO.general.JoystickControl import SimpleTwiprJoystickControl
from utils.network.network import getValidHostIP

logger = Logger('app')


def main():
    logger.info("Try hosting wireless network")
    result = hostNetwork("bilbo_net", "bilbobeutlin")
    if not result:
        logger.error("Hosted Configuration not possible")
        return

    logger.info("Wait for IP Address...")

    address = None
    for i in range(0, 10):
        address = getValidHostIP()
        if address:
            logger.info("Host IP Address: {}".format(address))
            break
        time.sleep(1)

    if address is None:
        logger.error("Host IP Address not possible. Please retry")

    app = SimpleTwiprJoystickControl()
    app.init()
    app.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()

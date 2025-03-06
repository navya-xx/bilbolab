import copy
import ctypes
import time

from matplotlib import pyplot as plt

from robot.bilbo import BILBO
from utils.logging_utils import setLoggerLevel, Logger
from utils.time import PerformanceTimer

setLoggerLevel('wifi', 'ERROR')

logger = Logger('main')
logger.setLevel('DEBUG')


def sample_callback(data, *args, **kwargs):
    ...


# HALLO
def main():
    bilbo = BILBO()
    bilbo.init()
    bilbo.start()

    time.sleep(30)

    num_samples = bilbo.logging.getNumSamples()
    timer = PerformanceTimer(print_output=True)

    data = bilbo.logging.getData(index_start=num_samples - 1000, index_end=num_samples, deepcopy=False, hdf5_only=True)
    timer.stop()
    # # samples_copy = copy.deepcopy(samples)
    #
    print(len(data))

    # plt.plot(data['general.time'], data['estimation.state.theta'])
    # plt.show()
    pass
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()

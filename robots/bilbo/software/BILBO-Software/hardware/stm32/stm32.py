import time
from RPi import GPIO

from hardware.board_config import getBoardConfig
from core.hardware.sx1508 import SX1508, SX1508_GPIO_MODE


def resetSTM32():
    board_config = getBoardConfig()

    if board_config['rev'] == 'rev3':
        raise NotImplementedError("Not implemented for rev3")

    elif board_config['rev'] == 'rev4':
        sx = SX1508(reset=False)
        sx.configureGPIO(gpio=board_config['pins']['stm32_reset']['pin'], mode=SX1508_GPIO_MODE.OUTPUT, pullup=False, pulldown=True)
        sx.writeGPIO(board_config['pins']['stm32_reset']['pin'], 1)
        time.sleep(1)
        sx.writeGPIO(board_config['pins']['stm32_reset']['pin'], 0)
        time.sleep(1)


if __name__ == '__main__':
    resetSTM32()
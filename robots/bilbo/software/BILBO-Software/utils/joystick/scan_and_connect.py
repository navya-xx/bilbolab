from utils.joystick.joystick_utils import scan_and_connect, remove_paired_device

if __name__ == '__main__':
    result = scan_and_connect(pattern='8BitDo')

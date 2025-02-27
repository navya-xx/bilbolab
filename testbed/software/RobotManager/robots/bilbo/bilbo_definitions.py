import enum

TWIPR_IDS = ['twipr1', 'twipr2', 'twipr3', 'twipr4', 'twipr5', 'twipr6', 'twipr7', 'twipr8', 'bilbo1', 'bilbo2', 'bilbo3']

TWIPR_REMOTE_STOP_COMMAND = "pkill -f 'python3 ./software/start_device.py'"
TWIPR_REMOTE_START_COMMAND = "python3 ./software/start_device.py"
TWIPR_USER_NAME = 'admin'
TWIPR_PASSWORD = 'beutlin'


class TWIPR_ControlMode(enum.IntEnum):
    TWIPR_CONTROL_MODE_OFF = 0,
    TWIPR_CONTROL_MODE_DIRECT = 1,
    TWIPR_CONTROL_MODE_BALANCING = 2,
    TWIPR_CONTROL_MODE_VELOCITY = 3

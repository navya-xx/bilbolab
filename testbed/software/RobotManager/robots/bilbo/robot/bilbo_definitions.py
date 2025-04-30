import enum

TWIPR_IDS = ['twipr1', 'twipr2', 'twipr3', 'twipr4', 'twipr5', 'twipr6', 'twipr7', 'twipr8', 'bilbo1', 'bilbo2',
             'bilbo3']

TWIPR_REMOTE_STOP_COMMAND = "pkill -f 'python3 ./software/start_device.py'"
TWIPR_REMOTE_START_COMMAND = "python3 ./software/start_device.py"
TWIPR_USER_NAME = 'admin'
TWIPR_PASSWORD = 'beutlin'


class BILBO_Control_Mode(enum.IntEnum):
    OFF = 0,
    DIRECT = 1,
    BALANCING = 2,
    VELOCITY = 3


BILBO_CONTROL_DT = 0.01
MAX_STEPS_TRAJECTORY = 3000

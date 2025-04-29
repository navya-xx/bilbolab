import dataclasses
import enum
import math
import time

import dacite
from dacite import from_dict


@dataclasses.dataclass
class TWIPR_Sample_General:
    id: str = ''
    status: str = ''
    configuration: str = ''
    time: float = 0
    tick: int = 0
    sample_time: float = 0


@dataclasses.dataclass
class TWIPR_Balancing_Control_Config:
    available: bool = False
    K: list = dataclasses.field(default_factory=list)  # State Feedback Gain
    u_lim: list = dataclasses.field(default_factory=list)  # Input Limits
    external_input_gain: list = dataclasses.field(
        default_factory=list)  # When using balancing control without speed control, this can scale the external input


@dataclasses.dataclass
class TWIPR_PID_Control_Config:
    Kp: float = 0
    Kd: float = 0
    Ki: float = 0
    anti_windup: float = 0
    integrator_saturation: float = None


@dataclasses.dataclass
class TWIPR_Speed_Control_Config:
    available: bool = False
    v: TWIPR_PID_Control_Config = dataclasses.field(default_factory=TWIPR_PID_Control_Config)
    psidot: TWIPR_PID_Control_Config = dataclasses.field(default_factory=TWIPR_PID_Control_Config)
    external_input_gain: list = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class TWIPR_Control_Config:
    name: str = ''
    description: str = ''
    balancing_control: TWIPR_Balancing_Control_Config = dataclasses.field(
        default_factory=TWIPR_Balancing_Control_Config)
    speed_control: TWIPR_Speed_Control_Config = dataclasses.field(default_factory=TWIPR_Speed_Control_Config)


class TWIPR_Control_Mode(enum.IntEnum):
    TWIPR_CONTROL_MODE_OFF = 0,
    TWIPR_CONTROL_MODE_DIRECT = 1,
    TWIPR_CONTROL_MODE_BALANCING = 2,
    TWIPR_CONTROL_MODE_VELOCITY = 3,
    TWIPR_CONTROL_MODE_POS = 4


class TWIPR_Control_Status(enum.IntEnum):
    TWIPR_CONTROL_STATE_ERROR = 0
    TWIPR_CONTROL_STATE_NORMAL = 1


class TWIPR_Control_Status_LL(enum.IntEnum):
    TWIPR_CONTROL_STATE_LL_ERROR = 0
    TWIPR_CONTROL_STATE_LL_NORMAL = 1


class TWIPR_Control_Mode_LL(enum.IntEnum):
    TWIPR_CONTROL_MODE_LL_OFF = 0,
    TWIPR_CONTROL_MODE_LL_DIRECT = 1,
    TWIPR_CONTROL_MODE_LL_BALANCING = 2,
    TWIPR_CONTROL_MODE_LL_VELOCITY = 3


@dataclasses.dataclass
class TWIPR_ControlInput:
    @dataclasses.dataclass
    class velocity:
        forward: float = 0
        turn: float = 0

    class balancing:
        u_left: float = 0
        u_right: float = 0

    class direct:
        u_left: float = 0
        u_right: float = 0


@dataclasses.dataclass
class TWIPR_Control_Sample:
    status: TWIPR_Control_Status = dataclasses.field(
        default=TWIPR_Control_Status(TWIPR_Control_Status.TWIPR_CONTROL_STATE_ERROR))
    mode: TWIPR_Control_Mode = dataclasses.field(default=TWIPR_Control_Mode(TWIPR_Control_Mode.TWIPR_CONTROL_MODE_OFF))
    configuration: str = ''
    input: TWIPR_ControlInput = dataclasses.field(default_factory=TWIPR_ControlInput)


@dataclasses.dataclass
class TWIPR_Estimation_State:
    x: float = 0
    y: float = 0
    v: float = 0
    theta: float = 0
    theta_dot: float = 0
    psi: float = 0
    psi_dot: float = 0


class TWIPR_Estimation_Status(enum.IntEnum):
    TWIPR_ESTIMATION_STATUS_ERROR = 0,
    TWIPR_ESTIMATION_STATUS_NORMAL = 1,


class TWIPR_Estimation_Mode(enum.IntEnum):
    TWIPR_ESTIMATION_MODE_VEL = 0,
    TWIPR_ESTIMATION_MODE_POS = 1


@dataclasses.dataclass
class TWIPR_Estimation_Sample:
    status: TWIPR_Estimation_Status = TWIPR_Estimation_Status.TWIPR_ESTIMATION_STATUS_ERROR
    state: TWIPR_Estimation_State = dataclasses.field(default_factory=TWIPR_Estimation_State)
    mode: TWIPR_Estimation_Mode = TWIPR_Estimation_Mode.TWIPR_ESTIMATION_MODE_VEL


class TWIPR_Drive_Status(enum.IntEnum):
    TWIPR_DRIVE_STATUS_OFF = 1,
    TWIPR_DRIVE_STATUS_ERROR = 0.
    TWIPR_DRIVE_STATUS_NORMAL = 2


@dataclasses.dataclass
class TWIPR_Drive_Data:
    status: TWIPR_Drive_Status = TWIPR_Drive_Status.TWIPR_DRIVE_STATUS_OFF
    torque: float = 0
    speed: float = 0
    input: float = 0


@dataclasses.dataclass
class TWIPR_Drive_Sample:
    left: TWIPR_Drive_Data = dataclasses.field(default_factory=TWIPR_Drive_Data)
    right: TWIPR_Drive_Data = dataclasses.field(default_factory=TWIPR_Drive_Data)


@dataclasses.dataclass
class TWIPR_Sensors_IMU:
    gyr: dict = dataclasses.field(default_factory=dict)
    acc: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class TWIPR_Sensors_Power:
    bat_voltage: float = 0
    bat_current: float = 0


@dataclasses.dataclass
class TWIPR_Sensors_Drive_Data:
    speed: float = 0
    torque: float = 0
    slip: bool = False


@dataclasses.dataclass
class TWIPR_Sensors_Drive:
    left: TWIPR_Sensors_Drive_Data = dataclasses.field(default_factory=TWIPR_Sensors_Drive_Data)
    right: TWIPR_Sensors_Drive_Data = dataclasses.field(default_factory=TWIPR_Sensors_Drive_Data)


@dataclasses.dataclass
class TWIPR_Sensors_Distance:
    front: float = 0
    back: float = 0


@dataclasses.dataclass
class TWIPR_Sensors_Sample:
    imu: TWIPR_Sensors_IMU = dataclasses.field(default_factory=TWIPR_Sensors_IMU)
    power: TWIPR_Sensors_Power = dataclasses.field(default_factory=TWIPR_Sensors_Power)
    drive: TWIPR_Sensors_Drive = dataclasses.field(default_factory=TWIPR_Sensors_Drive)
    distance: TWIPR_Sensors_Distance = dataclasses.field(default_factory=TWIPR_Sensors_Distance)


@dataclasses.dataclass
class TWIPR_Data:
    general: TWIPR_Sample_General = dataclasses.field(default_factory=TWIPR_Sample_General)
    control: TWIPR_Control_Sample = dataclasses.field(default_factory=TWIPR_Control_Sample)
    estimation: TWIPR_Estimation_Sample = dataclasses.field(default_factory=TWIPR_Estimation_Sample)
    drive: TWIPR_Drive_Sample = dataclasses.field(default_factory=TWIPR_Drive_Sample)
    sensors: TWIPR_Sensors_Sample = dataclasses.field(default_factory=TWIPR_Sensors_Sample)


type_hooks = {
    TWIPR_Control_Mode: TWIPR_Control_Mode,
    TWIPR_Control_Status: TWIPR_Control_Status,
    TWIPR_Control_Status_LL: TWIPR_Control_Status_LL,
    TWIPR_Control_Mode_LL: TWIPR_Control_Mode_LL,
    TWIPR_Estimation_Status: TWIPR_Estimation_Status,
    TWIPR_Estimation_Mode: TWIPR_Estimation_Mode,
    TWIPR_Drive_Status: TWIPR_Drive_Status
}


def twiprSampleFromDict(dict):
    sample = from_dict(data_class=TWIPR_Data, data=dict, config=dacite.Config(type_hooks=type_hooks))
    return sample


BILBO_STATE_DATA_DEFINITIONS = {
    'x': {
        'type': 'float',
        'unit': 'm',
        'max': 3,
        'min': -3,
        'display_resolution': '.1f'
    },
    'y': {
        'type': 'float',
        'unit': 'm',
        'max': 3,
        'min': -3,
        'display_resolution': '.1f'
    },
    'theta': {
        'type': 'float',
        'unit': 'rad',
        'max': math.pi / 2,
        'min': -math.pi / 2,
        'display_resolution': '.1f'
    },
    'theta_dot': {
        'type': 'float',
        'unit': 'rad/s',
        'max': 10,
        'min': -10,
        'display_resolution': '.1f'
    },
    'v': {
        'type': 'float',
        'unit': 'm/s',
        'max': 10,
        'min': -10,
        'display_resolution': '.1f'
    },
    'psi': {
        'type': 'float',
        'unit': 'rad',
        'max': math.pi,
        'min': -math.pi,
        'display_resolution': '.1f'
    },
    'psi_dot': {
        'type': 'float',
        'unit': 'rad/s',
        'max': 10,
        'min': -10,
        'display_resolution': '.1f'
    }
}

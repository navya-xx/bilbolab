import ctypes
import dataclasses
import enum
import time
from typing import Any, cast

from robot.communication.bilbo_communication import BILBO_Communication
from robot.control.definitions import BILBO_Control_Mode
from robot.lowlevel.stm32_sequencer import bilbo_sequence_input_t, bilbo_sequence_description_t, BILBO_Sequence_LL
import robot.lowlevel.stm32_addresses as addresses
from utils.callbacks import callback_handler, CallbackContainer
from utils.logging_utils import Logger, setLoggerLevel
from utils.ctypes_utils import struct_to_dataclass
from utils.dataclass_utils import from_dict
from paths import experiments_path

# ======================================================================================================================
logger = Logger('EXPERIMENT')
logger.setLevel('DEBUG')


# ======================================================================================================================
@dataclasses.dataclass
class BILBO_TrajectoryInput:
    step: int
    left: float
    right: float


# ======================================================================================================================
@dataclasses.dataclass
class BILBO_Trajectory:
    id: int
    name: str
    length: int
    inputs: dict[int, BILBO_TrajectoryInput]
    control_mode: BILBO_Control_Mode
    control_mode_end: BILBO_Control_Mode

    loaded: bool = False
    started: bool = False
    running: bool = False
    finished: bool = False
    aborted: bool = False


# TODO: ADD OUTPUTS TO THE TRAJECTORY

# === EXPERIMENT =======================================================================================================
class BILBO_Experiment_Type(enum.IntEnum):
    FREE = 1
    TRAJECTORY = 2
    MULTI_TRAJECTORY = 3


@dataclasses.dataclass
class BILBO_Experiment:
    name: str
    type: BILBO_Experiment_Type


# === CALLBACKS ========================================================================================================
@callback_handler
class BILBO_ExperimentCallbacks:
    trajectory_started: CallbackContainer
    trajectory_finished: CallbackContainer
    trajectory_aborted: CallbackContainer


# === BILBO_ExperimentHandler =========================================================================================
class BILBO_ExperimentHandler:
    communication: BILBO_Communication
    callbacks: BILBO_ExperimentCallbacks

    current_trajectory: BILBO_Trajectory = None

    def __init__(self, communication: BILBO_Communication):
        self.communication = communication
        self.callbacks = BILBO_ExperimentCallbacks()

    # ------------------------------------------------------------------------------------------------------------------
    def loadTrajectoryFromFile(self) -> BILBO_Trajectory:
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def saveTrajectoryToFile(self, trajectory: BILBO_Trajectory, filename: str):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def setTrajectory(self, trajectory: BILBO_Trajectory) -> bool:

        logger.debug(f"Setting trajectory {trajectory.id}")

        # First, check the trajectory length
        if trajectory.length != len(trajectory.inputs):
            logger.warning(f"Trajectory length does not match number of inputs. "
                           f"Trajectory length: {trajectory.length}, Number of inputs: {len(trajectory.inputs)}")
            return False

        # Load the trajectory data to the stm32
        success = self._setTrajectory_LL(trajectory)

        if not success:
            logger.warning("Failed to set trajectory")
            return False

        # Send the trajectory inputs via SPI
        input_data = self._trajectoryInputToBytes(trajectory.inputs)
        self.communication.spi.send(input_data)

        # Shortly wait
        time.sleep(0.01)

        # Read back the trajectory data
        trajectory_data = self._readTrajectoryData_LL()

        if trajectory_data is None:
            return False

        # Check if the trajectory data matches the trajectory and the inputs have been loaded
        if trajectory_data.sequence_id != trajectory.id or trajectory_data.length != trajectory.length:
            logger.warning(f"Trajectory data does not match the trajectory. "
                           f"Trajectory data: {trajectory_data}, Trajectory: {trajectory}")
            return False

        if not trajectory_data.loaded:
            logger.warning("Trajectory data has not been loaded")
            return False

        logger.info(f"Trajectory {trajectory.id} loaded")
        return True

    # ------------------------------------------------------------------------------------------------------------------
    def startTrajectory(self) -> bool:

        # First, check if a trajectory is loaded
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def update(self):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def getSample(self):
        sample = {}
        return sample

    # === PRIVATE METHODS ==============================================================================================
    def _setTrajectory_LL(self, trajectory: BILBO_Trajectory) -> bool:
        # Transform the trajectory into the corresponding ctypes structure

        sequence_description = bilbo_sequence_description_t(
            sequence_id=trajectory.id,
            length=trajectory.length,
            require_control_mode=False,
            wait_time_beginning=1,
            wait_time_end=1,
            control_mode=trajectory.control_mode.value,
            control_mode_end=trajectory.control_mode_end.value,
            loaded=False
        )

        # Send the trajectory to the STM32
        success = self.communication.serial.executeFunction(
            module=addresses.TWIPR_AddressTables.REGISTER_TABLE_GENERAL,
            address=addresses.TWIPR_SequencerAddresses.LOAD,
            data=sequence_description,
            input_type=bilbo_sequence_description_t,
            output_type=ctypes.c_bool,
            timeout=0.1
        )

        if not success:
            logger.warning(f'Failed to set trajectory {trajectory.id}')
            return False
        else:
            logger.debug(f'Trajectory data {trajectory.id} transferred')

        return True

    # ------------------------------------------------------------------------------------------------------------------
    def _readTrajectoryData_LL(self) -> BILBO_Sequence_LL:

        logger.debug("Get trajectory data")
        trajectory_data_struct = self.communication.serial.executeFunction(
            module=addresses.TWIPR_AddressTables.REGISTER_TABLE_GENERAL,
            address=addresses.TWIPR_SequencerAddresses.READ,
            data=None,
            input_type=None,
            output_type=bilbo_sequence_description_t,
            timeout=0.1
        )

        if trajectory_data_struct is None:
            logger.warning("Failed to get trajectory data")
            return None

        trajectory = from_dict(data=trajectory_data_struct, data_class=BILBO_Sequence_LL)

        return trajectory

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _trajectoryInputToBytes(trajectory_input: dict[int, BILBO_TrajectoryInput]) -> bytes:
        # Create a ctypes array type of the correct length

        ArrayType: Any = cast(Any, bilbo_sequence_input_t * len(trajectory_input))  # type: ignore
        c_array = ArrayType()  # Now this won't raise a warning

        # Populate the ctypes array with data from trajectory_input
        for i, inp in trajectory_input.items():
            c_array[i].step = inp.step
            c_array[i].u_1 = inp.left
            c_array[i].u_2 = inp.right

        # Get the byte representation of the array
        bytes_data = ctypes.string_at(ctypes.byref(c_array), ctypes.sizeof(c_array))
        return bytes_data

# ======================================================================================================================

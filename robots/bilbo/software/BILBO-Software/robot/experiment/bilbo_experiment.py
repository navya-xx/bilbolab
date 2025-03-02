import ctypes
import dataclasses
from typing import Any, cast

from robot.communication.bilbo_communication import BILBO_Communication
from robot.control.definitions import BILBO_Control_Mode
from robot.lowlevel.stm32_sequencer import bilbo_sequence_input_t, bilbo_sequence_description_t
import robot.lowlevel.stm32_addresses as addresses
from utils.logging_utils import Logger, setLoggerLevel

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


# === BILBO_ExperimentHandler =========================================================================================
class BILBO_ExperimentHandler:
    communication: BILBO_Communication

    def __init__(self, communication):
        self.communication = communication

    # ------------------------------------------------------------------------------------------------------------------
    def loadTrajectoryFromFile(self) -> BILBO_Trajectory:
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def saveTrajectoryToFile(self, trajectory: BILBO_Trajectory, filename: str):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def setTrajectory(self, trajectory: BILBO_Trajectory) -> bool:
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def runTrajectory(self) -> bool:
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def getTrajectoryData(self):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def update(self):
        ...

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
            logger.debug(f'Set trajectory {trajectory.id}')

        # self.communication.sp
        return True

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _trajectoryInputToBytes(trajectory_input: list[BILBO_TrajectoryInput]) -> bytes:
        # Create a ctypes array type of the correct length

        ArrayType: Any = cast(Any, bilbo_sequence_input_t * len(trajectory_input))  # type: ignore
        c_array = ArrayType()  # Now this won't raise a warning

        # Populate the ctypes array with data from trajectory_input
        for i, inp in enumerate(trajectory_input):
            c_array[i].step = inp.step
            c_array[i].u_1 = inp.left
            c_array[i].u_2 = inp.right

        # Get the byte representation of the array
        bytes_data = ctypes.string_at(ctypes.byref(c_array), ctypes.sizeof(c_array))
        return bytes_data


if __name__ == "__main__":
    # Create sample data
    inputs = [
        BILBO_TrajectoryInput(step=1, left=0.5, right=0.7),
        BILBO_TrajectoryInput(step=2, left=0.6, right=0.8),
    ]

    result_bytes = BILBO_ExperimentHandler._trajectoryInputToBytes(inputs)
    print(result_bytes)

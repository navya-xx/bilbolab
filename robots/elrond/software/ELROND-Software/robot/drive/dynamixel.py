from robot.communication.bilbo_communication import BILBO_Communication


class ELROND_Dynamixel_Handler:
    comm: BILBO_Communication

    def __init__(self, comm: BILBO_Communication):
        self.comm = comm

    def init(self) -> bool:
        success = self._checkMotors()

        return success

    def start(self):
        ...

    def setPosition(self):
        ...

    def readPositions(self):
        ...

    def _checkMotors(self) -> bool:
        ...

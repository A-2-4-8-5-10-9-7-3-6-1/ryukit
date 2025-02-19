import enum


class StateTransferSignal(int, enum.Enum):
    TRANSFERING = 0
    FAILED = 1

import enum


class StateTransferOp(str, enum.Enum):
    RESTORE = "restore"
    UPDATE = "update"

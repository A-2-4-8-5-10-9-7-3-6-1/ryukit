import enum


class TransferOp(str, enum.Enum):
    RESTORE = "restore"
    UPDATE = "update"

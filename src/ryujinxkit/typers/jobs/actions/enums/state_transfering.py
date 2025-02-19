import enum


class Enum(str, enum.Enum):
    RESTORE = "restore"
    UPDATE = "update"

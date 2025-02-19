import enum


class InstallSignal(int, enum.Enum):
    SERVICE_CONNECT = 0
    FAILED = 1
    DOWNLOADING = 2
    UNPACKING = 3

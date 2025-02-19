import enum


class ExtractSignal(int, enum.Enum):
    EXTRACTING = 0
    FAILED = 1
    READING = 2

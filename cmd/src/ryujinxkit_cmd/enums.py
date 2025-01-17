"""
Enum classes.

Dependency level: 0.
"""

from enum import Enum

# =============================================================================


class FileNode(Enum):
    USER_DATA = 0
    RYUJINX_DATA = 1
    RYUJINX_APP = 2
    RYUJINX_SYSTEM = 3
    RYUJINX_REGISTERED = 5
    APP_DATA = 6
    APP_STATE = 7
    APP_CONFIGS = 17
    DATABASE = 8
    SAVE_FOLDER = 9
    SAVE_COLLECTION = 10
    USER_SIDE_SYSTEM_SAVE = 11
    USER_SIDE_SAVE = 12
    USER_SIDE_SAVE_META = 13
    SYSTEM_SAVE = 14
    USER_SAVE = 15
    SAVE_META = 16


# -----------------------------------------------------------------------------


class Command(Enum):
    ROOT = 0
    SOURCE_RYUJINX = 1
    CREATE_SAVE = 2
    LIST_SAVES = 3
    SAVE = 4
    REMOVE_SAVE = 5
    USE_SAVE = 6
    RETAG = 7
    ARCHIVE = 8


# -----------------------------------------------------------------------------


class CustomColor(Enum):
    CREAM = 0


# -----------------------------------------------------------------------------


class UseOperation(Enum):
    RESTORE = 0
    UPDATE = 1


# =============================================================================

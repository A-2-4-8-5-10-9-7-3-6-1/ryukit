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
    RYUJINX_BIS = 4
    RYUJINX_REGISTERED = 5
    APP_DATA = 6
    APP_STATE = 7
    DATABASE = 8
    SAVE_FOLDER = 9
    SAVE_COLLECTION = 10
    SYSTEM_SAVE = 11
    USER_SAVE = 12
    USER_SAVE_META = 13


# -----------------------------------------------------------------------------


class Command(Enum):
    NULL = 0
    SOURCE_RYUJINX = 1


# =============================================================================

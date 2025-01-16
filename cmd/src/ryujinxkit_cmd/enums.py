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


# =============================================================================

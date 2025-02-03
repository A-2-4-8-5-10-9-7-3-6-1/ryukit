"""
- dependency level 0.
"""

from enum import Enum

# =============================================================================


class FileNode(Enum):
    """
    File-system nodes.
    """

    LOCAL_USER_DATA = 0

    RYUJINX_ROAMING_DATA = 1
    RYUJINX_LOCAL_DATA = 2
    RYUJINX_SYSTEM = 3
    RYUJINX_REGISTERED = 5
    RYUJINX_SYSTEM_SAVE = 14
    RYUJINX_USER_SAVE = 15
    RYUJINX_SAVE_META = 16

    RYUJINXKIT_ROAMING_DATA = 6
    RYUJINXKIT_CONFIGS = 17
    RYUJINXKIT_DATABASE = 8
    RYUJINXKIT_SAVE_FOLDER = 9
    RYUJINXKIT_SAVE_INSTANCE_FOLDER = 10
    RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE = 11
    RYUJINXKIT_SAVE_INSTANCE_SAVE = 12
    RYUJINXKIT_SAVE_INSTANCE_SAVE_META = 13


# -----------------------------------------------------------------------------


class RyujinxKitCommand(Enum):
    """
    Service commands.
    """

    RYUJINXKIT = 0

    RYUJINXKIT_SOURCE = 1
    RYUJINXKIT_SAVE = 4
    RYUJINXKIT_VERSION = 11

    RYUJINXKIT_SAVE_CREATE = 2
    RYUJINXKIT_SAVE_LIST = 3
    RYUJINXKIT_SAVE_REMOVE = 5
    RYUJINXKIT_SAVE_UPDATE = 6
    RYUJINXKIT_SAVE_RETAG = 7
    RYUJINXKIT_SAVE_EXPORT = 8
    RYUJINXKIT_SAVE_EXTRACT = 9
    RYUJINXKIT_SAVE_RESTORE = 10


# =============================================================================

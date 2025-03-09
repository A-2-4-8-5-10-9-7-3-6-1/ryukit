"""path_resolver-related definitions.

Exports
-------
- :class:`Node`: The complete collection of file-system nodes.
- resolver: App's resolver object.
"""

import enum
import importlib
import importlib.metadata

import path_resolve
import platformdirs


class Node(int, enum.Enum):
    LOCAL_USER_DATA = 0

    RYUJINX_ROAMING_DATA = 1
    RYUJINX_LOCAL_DATA = 2
    RYUJINX_SYSTEM = 3
    RYUJINX_REGISTERED = 5
    RYUJINX_SYSTEM_SAVE = 14
    RYUJINX_USER_SAVE = 15
    RYUJINX_SAVE_META = 16

    RYUJINXKIT_ROAMING_DATA = 6
    RYUJINXKIT_DATABASE = 8
    RYUJINXKIT_SAVE_FOLDER = 9
    RYUJINXKIT_SAVE_INSTANCE_FOLDER = 10
    RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE = 11
    RYUJINXKIT_SAVE_INSTANCE_SAVE = 12
    RYUJINXKIT_SAVE_INSTANCE_SAVE_META = 13


resolver = path_resolve.Resolver(
    nodes={
        Node.RYUJINX_LOCAL_DATA: {
            "parent": Node.LOCAL_USER_DATA,
            "cache": True,
        },
        Node.RYUJINX_SYSTEM: {
            "parent": Node.RYUJINX_ROAMING_DATA,
            "cache": True,
            "tail": "system",
        },
        Node.RYUJINX_REGISTERED: {
            "parent": Node.RYUJINX_ROAMING_DATA,
            "tail": "bis/system/Contents/registered",
        },
        Node.RYUJINXKIT_DATABASE: {
            "parent": Node.RYUJINXKIT_ROAMING_DATA,
            "cache": True,
            "tail": "database.db",
        },
        Node.RYUJINXKIT_SAVE_FOLDER: {
            "parent": Node.RYUJINXKIT_ROAMING_DATA,
            "cache": True,
            "tail": "saves",
        },
        Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER: {
            "parent": Node.RYUJINXKIT_SAVE_FOLDER
        },
        Node.RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE: {
            "parent": Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
            "tail": "system",
        },
        Node.RYUJINXKIT_SAVE_INSTANCE_SAVE: {
            "parent": Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
            "tail": "user",
        },
        Node.RYUJINXKIT_SAVE_INSTANCE_SAVE_META: {
            "parent": Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
            "tail": "meta",
        },
        Node.RYUJINX_SYSTEM_SAVE: {
            "parent": Node.RYUJINX_ROAMING_DATA,
            "cache": True,
            "tail": "bis/system/save",
        },
        Node.RYUJINX_USER_SAVE: {
            "parent": Node.RYUJINX_ROAMING_DATA,
            "cache": True,
            "tail": "bis/user/save",
        },
        Node.RYUJINX_SAVE_META: {
            "parent": Node.RYUJINX_ROAMING_DATA,
            "cache": True,
            "tail": "bis/user/saveMeta",
        },
    },
    basics={
        Node.LOCAL_USER_DATA: platformdirs.user_data_path(),
        Node.RYUJINX_ROAMING_DATA: platformdirs.PlatformDirs(
            appname="Ryujinx", appauthor=False, roaming=True
        ).user_data_path,
        Node.RYUJINXKIT_ROAMING_DATA: platformdirs.PlatformDirs(
            appname="RyujinxKit",
            appauthor=importlib.metadata.metadata("ryujinxkit")["Author"],
            roaming=True,
        ).user_data_path,
    },
)

import importlib.metadata

import path_resolve
import platformdirs

from .resolver_node import ResolverNode

resolver = path_resolve.Resolver(
    nodes={
        ResolverNode.RYUJINX_LOCAL_DATA: {
            "parent": ResolverNode.LOCAL_USER_DATA,
            "cache": True,
        },
        ResolverNode.RYUJINX_SYSTEM: {
            "parent": ResolverNode.RYUJINX_ROAMING_DATA,
            "cache": True,
            "tail": "system",
        },
        ResolverNode.RYUJINX_REGISTERED: {
            "parent": ResolverNode.RYUJINX_ROAMING_DATA,
            "tail": "bis/system/Contents/registered",
        },
        ResolverNode.RYUJINXKIT_DATABASE: {
            "parent": ResolverNode.RYUJINXKIT_ROAMING_DATA,
            "cache": True,
            "tail": "database.db",
        },
        ResolverNode.RYUJINXKIT_SAVE_FOLDER: {
            "parent": ResolverNode.RYUJINXKIT_ROAMING_DATA,
            "cache": True,
            "tail": "saves",
        },
        ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER: {
            "parent": ResolverNode.RYUJINXKIT_SAVE_FOLDER
        },
        ResolverNode.RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE: {
            "parent": ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
            "tail": "system",
        },
        ResolverNode.RYUJINXKIT_SAVE_INSTANCE_SAVE: {
            "parent": ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
            "tail": "user",
        },
        ResolverNode.RYUJINXKIT_SAVE_INSTANCE_SAVE_META: {
            "parent": ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
            "tail": "meta",
        },
        ResolverNode.RYUJINX_SYSTEM_SAVE: {
            "parent": ResolverNode.RYUJINX_ROAMING_DATA,
            "cache": True,
            "tail": "bis/system/save",
        },
        ResolverNode.RYUJINX_USER_SAVE: {
            "parent": ResolverNode.RYUJINX_ROAMING_DATA,
            "cache": True,
            "tail": "bis/user/save",
        },
        ResolverNode.RYUJINX_SAVE_META: {
            "parent": ResolverNode.RYUJINX_ROAMING_DATA,
            "cache": True,
            "tail": "bis/user/saveMeta",
        },
    },
    basics={
        ResolverNode.LOCAL_USER_DATA: platformdirs.user_data_path(),
        ResolverNode.RYUJINX_ROAMING_DATA: platformdirs.PlatformDirs(
            appname="Ryujinx",
            appauthor=False,
            roaming=True,
        ).user_data_path,
        ResolverNode.RYUJINXKIT_ROAMING_DATA: platformdirs.PlatformDirs(
            appname="RyujinxKit",
            appauthor=importlib.metadata.metadata("ryujinxkit")["Author"],
            roaming=True,
        ).user_data_path,
    },
)

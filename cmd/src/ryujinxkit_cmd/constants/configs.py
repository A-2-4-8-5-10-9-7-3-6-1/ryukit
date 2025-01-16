"""
Configuration constants.

Dependency level: 1.
"""

from hrchypth_resolver import Node, Resolver
from platformdirs import PlatformDirs, user_data_path

from ..enums import FileNode

# =============================================================================

SETUP_CHUNK_SIZE = pow(2, 12)

SETUP_CONNECTION_ERROR_MESSAGE = "Couldn't connect to server."
UNPACK_SLOWDOWN: dict[str, float] = {
    "app-files": 0.2,
    "system-keys": 1,
    "system-registered": 0.01,
}

# -----------------------------------------------------------------------------

RESOLVER = (
    lambda ryujinx_pd=PlatformDirs(
        appname="Ryujinx",
        appauthor=False,
        roaming=True,
    ), app_pd=PlatformDirs(
        appname="RyujinxKit",
        appauthor="A-2-4-8-5-10-9-7-3-6-1",
        roaming=False,
    ): Resolver[
        FileNode
    ](
        nodes=[
            (
                FileNode.RYUJINX_APP,
                Node(parent=FileNode.USER_DATA, cache=True),
            ),
            (
                FileNode.RYUJINX_SYSTEM,
                Node(parent=FileNode.RYUJINX_DATA, cache=True, tail="system"),
            ),
            (
                FileNode.RYUJINX_BIS,
                Node(parent=FileNode.RYUJINX_DATA, cache=True, tail="bis"),
            ),
            (
                FileNode.RYUJINX_REGISTERED,
                Node(
                    parent=FileNode.RYUJINX_BIS,
                    tail="system/Contents/registered",
                ),
            ),
            (
                FileNode.APP_STATE,
                Node(parent=FileNode.APP_DATA, cache=True, tail="state.json"),
            ),
        ],
        primitives=[
            (FileNode.USER_DATA, user_data_path(roaming=True)),
            (FileNode.RYUJINX_DATA, ryujinx_pd.user_data_path),
            (FileNode.APP_DATA, app_pd.user_data_path),
        ],
    )
)()

# -----------------------------------------------------------------------------

[
    RESOLVER(id_=id_).mkdir(parents=True, exist_ok=True)
    for id_ in [FileNode.APP_DATA, FileNode.RYUJINX_DATA]
]

# =============================================================================

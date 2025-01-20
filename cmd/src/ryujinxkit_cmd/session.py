"""
Session-management class.

Dependency level: 1.
"""

from importlib.resources import files
from sqlite3 import Cursor, connect
from typing import Any

from hrchypth_resolver import Node, Resolver
from platformdirs import PlatformDirs, user_data_path

from .constants.configs import APP_NAME, AUTHOR
from .enums import FileNode

# =============================================================================


class _Meta(type):
    """
    Metaclass for `Session`.

    :attr RESOLVER: Path resolver.
    :attr database_cursor: Database cursor.
    """

    RESOLVER: Resolver[FileNode]
    database_cursor: Cursor

    # -------------------------------------------------------------------------

    def __enter__(cls) -> None:
        """
        Initialize session.
        """

        [
            cls.RESOLVER(id_=id_).mkdir(parents=True, exist_ok=True)
            for id_ in [
                FileNode.APP_DATA,
                FileNode.RYUJINX_DATA,
                FileNode.SAVE_FOLDER,
                FileNode.APP_CONFIGS,
            ]
        ]

        cls.database_cursor = connect(
            database=cls.RESOLVER(id_=FileNode.DATABASE),
            autocommit=False,
        ).cursor()

        cls.database_cursor.executescript(
            (
                files(anchor="ryujinxkit_cmd")
                / "assets"
                / "sql"
                / "tables.sql"
            ).read_text()
        )

    # -------------------------------------------------------------------------

    def __exit__(cls, *_: Any) -> None:
        """
        Closes session.
        """

        cls.database_cursor.connection.close()


# -----------------------------------------------------------------------------


class Session(metaclass=_Meta):
    """
    Session-management class.
    """

    RESOLVER = (
        lambda ryujinx_pd, app_pd: Resolver(
            nodes={
                FileNode.RYUJINX_APP: Node(
                    parent=FileNode.USER_DATA,
                    cache=True,
                ),
                FileNode.RYUJINX_SYSTEM: Node(
                    parent=FileNode.RYUJINX_DATA,
                    cache=True,
                    tail="system",
                ),
                FileNode.RYUJINX_REGISTERED: Node(
                    parent=FileNode.RYUJINX_DATA,
                    tail="bis/system/Contents/registered",
                ),
                FileNode.DATABASE: Node(
                    parent=FileNode.APP_DATA,
                    cache=True,
                    tail="database-sqlite3.db",
                ),
                FileNode.SAVE_FOLDER: Node(
                    parent=FileNode.APP_DATA,
                    cache=True,
                    tail="states",
                ),
                FileNode.SAVE_COLLECTION: Node(parent=FileNode.SAVE_FOLDER),
                FileNode.USER_SIDE_SYSTEM_SAVE: Node(
                    parent=FileNode.SAVE_COLLECTION,
                    tail="system",
                ),
                FileNode.USER_SIDE_SAVE: Node(
                    parent=FileNode.SAVE_COLLECTION,
                    tail="user",
                ),
                FileNode.USER_SIDE_SAVE_META: Node(
                    parent=FileNode.SAVE_COLLECTION,
                    tail="meta",
                ),
                FileNode.SYSTEM_SAVE: Node(
                    parent=FileNode.RYUJINX_DATA,
                    cache=True,
                    tail="bis/system/save",
                ),
                FileNode.USER_SAVE: Node(
                    parent=FileNode.RYUJINX_DATA,
                    cache=True,
                    tail="bis/user/save",
                ),
                FileNode.SAVE_META: Node(
                    parent=FileNode.RYUJINX_DATA,
                    cache=True,
                    tail="bis/user/saveMeta",
                ),
            },
            primitives={
                FileNode.USER_DATA: user_data_path(),
                FileNode.RYUJINX_DATA: ryujinx_pd.user_data_path,
                FileNode.APP_DATA: app_pd.user_data_path,
                FileNode.APP_CONFIGS: app_pd.user_config_path,
            },
        )
    )(
        PlatformDirs(appname="Ryujinx", appauthor=False, roaming=True),
        PlatformDirs(appname=APP_NAME, appauthor=AUTHOR, roaming=False),
    )

    # -------------------------------------------------------------------------

    def __init__(self):
        raise NotImplementedError


# =============================================================================

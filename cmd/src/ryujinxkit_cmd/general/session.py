"""
- dependency level 1.
"""

from sqlite3 import Cursor, connect
from typing import Any

from hyrchy_pthresolver import Node, Resolver
from platformdirs import PlatformDirs, user_data_path

from .constants.configs import (
    RYUJINX_AUTHOR,
    RYUJINX_NAME,
    RYUJINX_ROAMING,
    RYUJINXKIT_AUTHOR,
    RYUJINXKIT_NAME,
    RYUJINXKIT_ROAMING,
    RYUJINXKIT_VERSION,
)
from .enums import FileNode

# =============================================================================


class _Meta(type):
    """
    Metaclass for `Session`.
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
                FileNode.RYUJINXKIT_DATA,
                FileNode.RYUJINX_DATA,
                FileNode.RYUJINXKIT_SAVE_FOLDER,
                FileNode.RYUJINXKIT_CONFIGS,
            ]
        ]

        cls.database_cursor = connect(
            database=cls.RESOLVER(id_=FileNode.RYUJINXKIT_DATABASE),
            autocommit=False,
        ).cursor()

        cls.database_cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS saves (
                id INTEGER,
                tag VARCHAR(20) DEFAULT untagged,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used TIMESTAMP,
                size INTEGER DEFAULT 0,
                PRIMARY KEY (id)
            );
            """
        )

    # -------------------------------------------------------------------------

    def __exit__(cls, *_: Any) -> None:
        """
        Close session.
        """

        cls.database_cursor.connection.commit()
        cls.database_cursor.connection.close()


# -----------------------------------------------------------------------------


class Session(metaclass=_Meta):
    """
    Session-management class.

    :attr RESOLVER: Path resolver.
    :attr database_cursor: Database cursor.
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
                FileNode.RYUJINXKIT_DATABASE: Node(
                    parent=FileNode.RYUJINXKIT_DATA,
                    cache=True,
                    tail="metadata.db",
                ),
                FileNode.RYUJINXKIT_SAVE_FOLDER: Node(
                    parent=FileNode.RYUJINXKIT_DATA,
                    cache=True,
                    tail="states",
                ),
                FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER: Node(
                    parent=FileNode.RYUJINXKIT_SAVE_FOLDER
                ),
                FileNode.RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE: Node(
                    parent=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                    tail="system",
                ),
                FileNode.RYUJINXKIT_SAVE_INSTANCE_SAVE: Node(
                    parent=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                    tail="user",
                ),
                FileNode.RYUJINXKIT_SAVE_INSTANCE_SAVE_META: Node(
                    parent=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                    tail="meta",
                ),
                FileNode.RYUJINX_SYSTEM_SAVE: Node(
                    parent=FileNode.RYUJINX_DATA,
                    cache=True,
                    tail="bis/system/save",
                ),
                FileNode.RYUJINX_USER_SAVE: Node(
                    parent=FileNode.RYUJINX_DATA,
                    cache=True,
                    tail="bis/user/save",
                ),
                FileNode.RYUJINX_SAVE_META: Node(
                    parent=FileNode.RYUJINX_DATA,
                    cache=True,
                    tail="bis/user/saveMeta",
                ),
            },
            primitives={
                FileNode.USER_DATA: user_data_path(),
                FileNode.RYUJINX_DATA: ryujinx_pd.user_data_path,
                FileNode.RYUJINXKIT_DATA: app_pd.user_data_path,
                FileNode.RYUJINXKIT_CONFIGS: app_pd.user_config_path,
            },
        )
    )(
        PlatformDirs(
            appname=RYUJINX_NAME,
            appauthor=RYUJINX_AUTHOR,
            roaming=RYUJINX_ROAMING,
        ),
        PlatformDirs(
            appname=RYUJINXKIT_NAME,
            appauthor=RYUJINXKIT_AUTHOR,
            roaming=RYUJINXKIT_ROAMING,
            version=RYUJINXKIT_VERSION,
        ),
    )

    # -------------------------------------------------------------------------

    def __init__(self):
        raise NotImplementedError


# =============================================================================

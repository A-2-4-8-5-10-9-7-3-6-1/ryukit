"""
- dependency level 1.
"""

from io import StringIO
from sqlite3 import Cursor, connect
from typing import Any, ClassVar, Never

from hyrchy_pthresolver import Resolver
from platformdirs import PlatformDirs, user_data_path
from rich.console import Console

from .configs import APP_AUTHOR, RYUJINX_AUTHOR
from .enums import FileNode

# =============================================================================


class _Meta(type):
    """
    Metaclass for `Session`.
    """

    resolver: Resolver[FileNode]
    database_cursor: Cursor
    null_buffer: StringIO

    # -------------------------------------------------------------------------

    def __enter__(cls) -> None:
        """
        Initialize session.
        """

        [
            cls.resolver(id_=id_).mkdir(parents=True, exist_ok=True)
            for id_ in [
                FileNode.RYUJINXKIT_ROAMING_DATA,
                FileNode.RYUJINX_ROAMING_DATA,
                FileNode.RYUJINXKIT_SAVE_FOLDER,
                FileNode.RYUJINXKIT_CONFIGS,
            ]
        ]

        cls.database_cursor = connect(
            database=cls.resolver(id_=FileNode.RYUJINXKIT_DATABASE),
            autocommit=False,
        ).cursor()
        cls.null_buffer = StringIO()

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
        cls.null_buffer.close()


# -----------------------------------------------------------------------------


class Session(metaclass=_Meta):
    """
    Session-management class.

    :attr resolver: Path resolver.
    :attr database_cursor: Database cursor.
    :attr console: Main console.
    :attr null_buffer: Buffer for hidden output.
    """

    console: ClassVar[Console] = Console(highlight=False)
    resolver: ClassVar[Resolver[FileNode]] = (
        lambda ryujinx_rpd, ryujinxkit_rpd: Resolver(
            leaves={
                FileNode.RYUJINX_LOCAL_DATA: {
                    "parent": FileNode.LOCAL_USER_DATA,
                    "cache": True,
                },
                FileNode.RYUJINX_SYSTEM: {
                    "parent": FileNode.RYUJINX_ROAMING_DATA,
                    "cache": True,
                    "tail": "system",
                },
                FileNode.RYUJINX_REGISTERED: {
                    "parent": FileNode.RYUJINX_ROAMING_DATA,
                    "tail": "bis/system/Contents/registered",
                },
                FileNode.RYUJINXKIT_DATABASE: {
                    "parent": FileNode.RYUJINXKIT_ROAMING_DATA,
                    "cache": True,
                    "tail": "metadata.db",
                },
                FileNode.RYUJINXKIT_SAVE_FOLDER: {
                    "parent": FileNode.RYUJINXKIT_ROAMING_DATA,
                    "cache": True,
                    "tail": "states",
                },
                FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER: {
                    "parent": FileNode.RYUJINXKIT_SAVE_FOLDER
                },
                FileNode.RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE: {
                    "parent": FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                    "tail": "system",
                },
                FileNode.RYUJINXKIT_SAVE_INSTANCE_SAVE: {
                    "parent": FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                    "tail": "user",
                },
                FileNode.RYUJINXKIT_SAVE_INSTANCE_SAVE_META: {
                    "parent": FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                    "tail": "meta",
                },
                FileNode.RYUJINX_SYSTEM_SAVE: {
                    "parent": FileNode.RYUJINX_ROAMING_DATA,
                    "cache": True,
                    "tail": "bis/system/save",
                },
                FileNode.RYUJINX_USER_SAVE: {
                    "parent": FileNode.RYUJINX_ROAMING_DATA,
                    "cache": True,
                    "tail": "bis/user/save",
                },
                FileNode.RYUJINX_SAVE_META: {
                    "parent": FileNode.RYUJINX_ROAMING_DATA,
                    "cache": True,
                    "tail": "bis/user/saveMeta",
                },
            },
            basics={
                FileNode.LOCAL_USER_DATA: user_data_path(),
                FileNode.RYUJINX_ROAMING_DATA: ryujinx_rpd.user_data_path,
                FileNode.RYUJINXKIT_ROAMING_DATA: ryujinxkit_rpd.user_data_path,
                FileNode.RYUJINXKIT_CONFIGS: ryujinxkit_rpd.user_config_path,
            },
        )
    )(
        PlatformDirs(
            appname="Ryujinx",
            appauthor=RYUJINX_AUTHOR,
            roaming=True,
        ),
        PlatformDirs(
            appname="RyujinxKit",
            appauthor=APP_AUTHOR,
            roaming=True,
        ),
    )

    # -------------------------------------------------------------------------

    def __init__(self) -> Never:
        """
        :raises: `NotImplementedError` if invoked.
        """

        raise NotImplementedError


# =============================================================================

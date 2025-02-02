"""
- dependency level 2
"""

from pathlib import Path
from time import sleep

from parser_generator import Command as ParserCommand
from parser_generator import generate
from rich.box import Box
from rich.console import Console
from rich.table import Table

from src.general import (
    DATABASE_INSERT_BUFFER,
    DATABASE_SAVE_TAG_DEFAULT,
    RYUJINXKIT_NAME,
    RYUJINXKIT_VERSION,
    Command,
    FileNode,
    Session,
)

from ...data import archive, read_archive, remove_save, source, use_save
from ..constants.configs import (
    COLOR_CREAM,
    DEFAULT_ARCHIVE_NAME,
    RYUJINXKIT_PROG_NAME,
)
from .sanitization import sanitize

# =============================================================================


def start() -> None:
    """
    Begin ui.
    """

    console = Console()

    with Session:
        generate(
            function_attr="func",
            commands={
                Command.RYUJINXKIT: ParserCommand(
                    parser_args={
                        "prog": RYUJINXKIT_PROG_NAME,
                        "description": "A tool for Ryujinx (for Windows) "
                        "management.",
                    },
                    subparsers_args={
                        "title": "commands",
                        "required": True,
                    },
                    parent=Command.RYUJINXKIT,
                ),
                Command.RYUJINXKIT_VERSION: ParserCommand(
                    parser_args={
                        "name": "version",
                        "help": "Show version and quit",
                    },
                    parent=Command.RYUJINXKIT,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_VERSION,
                            function=lambda _: print(
                                f"{RYUJINXKIT_NAME} version "
                                + RYUJINXKIT_VERSION
                            ),
                        )
                    },
                ),
                Command.RYUJINXKIT_SAVE: ParserCommand(
                    parser_args={
                        "name": "save",
                        "help": "Save-state usage commands",
                        "aliases": ["sv"],
                    },
                    subparsers_args={
                        "title": "commands",
                        "required": True,
                    },
                    parent=Command.RYUJINXKIT,
                ),
                Command.RYUJINXKIT_SOURCE: ParserCommand(
                    parser_args={
                        "name": "install",
                        "help": "Install and ready Ryujinx",
                        "aliases": ["source"],
                    },
                    params=[
                        {
                            "dest": "url",
                            "help": "Download URL (obtained from an authority)",
                            "type": str,
                        }
                    ],
                    parent=Command.RYUJINXKIT,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_SOURCE,
                            function=lambda args: [
                                source(url=args.url),
                                console.print(
                                    f"[{COLOR_CREAM}]"
                                    "Installed to: "
                                    + str(
                                        Session.RESOLVER(
                                            id_=FileNode.RYUJINX_LOCAL_DATA
                                        )
                                    )
                                    + f".[/{COLOR_CREAM}]",
                                    highlight=False,
                                ),
                            ],
                        )
                    },
                ),
                Command.RYUJINXKIT_SAVE_CREATE: ParserCommand(
                    parser_args={
                        "name": "create",
                        "help": "Create a new save state--it will be empty",
                    },
                    params=[
                        (
                            ["-t", "--tag"],
                            {
                                "help": "A tag for your save state",
                                "type": str,
                            },
                        )
                    ],
                    parent=Command.RYUJINXKIT_SAVE,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_SAVE_CREATE,
                            function=lambda args: [
                                Session.database_cursor.execute(
                                    """
                                    INSERT INTO saves (tag)
                                    VALUES (?);
                                    """,
                                    [args.tag],
                                ),
                                sleep(DATABASE_INSERT_BUFFER),
                                console.print(
                                    f"[{COLOR_CREAM}]Save ID: "
                                    + str(Session.database_cursor.lastrowid)
                                    + f".[/{COLOR_CREAM}]"
                                ),
                            ],
                        ),
                        "tag": DATABASE_SAVE_TAG_DEFAULT,
                    },
                ),
                Command.RYUJINXKIT_SAVE_LIST: ParserCommand(
                    parser_args={
                        "name": "list",
                        "aliases": ["ls"],
                        "help": "List your save states",
                    },
                    parent=Command.RYUJINXKIT_SAVE,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_SAVE_LIST,
                            function=lambda _, table=Table(
                                "ID",
                                "TAG",
                                "CREATED",
                                "UPDATED",
                                "USED",
                                "SIZE",
                                box=Box(
                                    box="    \n"
                                    "    \n"
                                    " -  \n"
                                    "    \n"
                                    "    \n"
                                    "    \n"
                                    "    \n"
                                    "    \n",
                                    ascii=True,
                                ),
                            ): [
                                [
                                    table.add_row(*row)
                                    for row in Session.database_cursor.execute(
                                        """
                                        SELECT 
                                            CAST(id AS TEXT),
                                            CAST(tag AS TEXT),
                                            CAST(created AS TEXT),
                                            CAST(updated AS TEXT),
                                            CAST(
                                                COALESCE(used, "Never")
                                                AS text
                                            ),
                                            CAST(
                                                ROUND(
                                                    size / (1024 * 1024.0),
                                                    2
                                                )
                                                AS TEXT
                                            )
                                            || "MB"
                                        FROM saves
                                        ORDER BY
                                            used DESC,
                                            updated DESC, 
                                            created DESC;
                                        """
                                    ).fetchall()
                                ],
                                console.print(table),
                            ],
                        )
                    },
                ),
                Command.RYUJINXKIT_SAVE_REMOVE: ParserCommand(
                    parser_args={
                        "name": "remove",
                        "aliases": ["rm"],
                        "help": "Remove a save state",
                    },
                    params=[
                        {
                            "help": "The save-state's ID",
                            "type": str,
                            "dest": "id",
                        }
                    ],
                    parent=Command.RYUJINXKIT_SAVE,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_SAVE_REMOVE,
                            function=lambda args: remove_save(id_=args.id),
                        )
                    },
                ),
                Command.RYUJINXKIT_SAVE_UPDATE: ParserCommand(
                    parser_args={
                        "name": "update",
                        "help": "Update a save state with the current "
                        "environment of your Ryujinx installation",
                    },
                    params=[
                        {
                            "dest": "id",
                            "help": "ID of save state",
                            "type": str,
                        }
                    ],
                    parent=Command.RYUJINXKIT_SAVE,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_SAVE_UPDATE,
                            function=lambda args: use_save(
                                id_=args.id,
                                operation="update",
                            ),
                        )
                    },
                ),
                Command.RYUJINXKIT_SAVE_RESTORE: ParserCommand(
                    parser_args={
                        "name": "restore",
                        "help": "Restore your Ryujinx environment "
                        "from a save state",
                    },
                    params=[
                        {
                            "dest": "id",
                            "help": "ID of save state",
                            "type": str,
                        }
                    ],
                    parent=Command.RYUJINXKIT_SAVE,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_SAVE_RESTORE,
                            function=lambda args: use_save(
                                id_=args.id,
                                operation="restore",
                            ),
                        )
                    },
                ),
                Command.RYUJINXKIT_SAVE_RETAG: ParserCommand(
                    parser_args={
                        "name": "retag",
                        "help": "Change the tag of a save-state",
                        "aliases": ["rt"],
                    },
                    params=[
                        {
                            "help": "Save-state's ID",
                            "dest": "id",
                            "type": str,
                        },
                        {
                            "dest": "tag",
                            "type": str,
                            "help": "A new tag for the save state",
                        },
                    ],
                    parent=Command.RYUJINXKIT_SAVE,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_SAVE_RETAG,
                            function=lambda args: (
                                Session.database_cursor.execute(
                                    """
                                    UPDATE saves
                                    SET tag = ?, updated = datetime("now")
                                    WHERE id = ?;
                                    """,
                                    [args.tag, args.id],
                                )
                            ),
                        )
                    },
                ),
                Command.RYUJINXKIT_SAVE_EXPORT: ParserCommand(
                    parser_args={
                        "name": "export",
                        "help": "Export your save states as a tar file",
                        "aliases": ["archive"],
                    },
                    params=[
                        (
                            ["-o", "--output"],
                            {
                                "help": "Output-file name--default is "
                                + DEFAULT_ARCHIVE_NAME,
                                "type": str,
                            },
                        )
                    ],
                    parent=Command.RYUJINXKIT_SAVE,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_SAVE_EXPORT,
                            function=lambda args: archive(output=args.output),
                        ),
                        "output": DEFAULT_ARCHIVE_NAME,
                    },
                ),
                Command.RYUJINXKIT_SAVE_EXTRACT: ParserCommand(
                    parser_args={
                        "name": "extract",
                        "help": "Extract save states from an export",
                        "aliases": ["read"],
                    },
                    params=[
                        {
                            "dest": "path",
                            "help": "Path to your extract",
                            "type": Path,
                        }
                    ],
                    parent=Command.RYUJINXKIT_SAVE,
                    defaults={
                        "func": sanitize(
                            command=Command.RYUJINXKIT_SAVE_EXTRACT,
                            function=lambda args: read_archive(path=args.path),
                        )
                    },
                ),
            },
        )[1]()


# =============================================================================

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

from ...data import archive, read_archive, remove_save, source, use_save
from ...general import (
    DATABASE_INSERT_BUFFER,
    DATABASE_SAVE_TAG_DEFAULT,
    Command,
    FileNode,
    Session,
)
from ...general.constants.configs import RYUJINXKIT_NAME, RYUJINXKIT_VERSION
from ..constants.configs import (
    COLOR_CREAM,
    DEFAULT_ARCHIVE_NAME,
    RYUJINXKIT_PROG_NAME,
)
from .sanitization import sanitize

# =============================================================================


def main() -> None:
    """
    Entry point.
    """

    console = Console()
    _begin = generate(
        function_attr="func",
        commands={
            Command.RYUJINXKIT: ParserCommand(
                parser_args={
                    "prog": RYUJINXKIT_PROG_NAME,
                    "description": "Ryujinx-management toolkit.",
                },
                subparsers_args={
                    "title": "commands",
                },
                params=[
                    (
                        ["--version"],
                        {
                            "action": "store_true",
                            "help": "Show version",
                        },
                    )
                ],
                parent=Command.RYUJINXKIT,
                defaults={
                    "func": sanitize(
                        command=Command.RYUJINXKIT,
                        function=lambda args: (
                            print(
                                f"{RYUJINXKIT_NAME} version {RYUJINXKIT_VERSION}"
                            )
                            if args.version
                            else None
                        ),
                    )
                },
            ),
            Command.RYUJINXKIT_SAVE: ParserCommand(
                parser_args={
                    "name": "save",
                    "description": "Save-state management tools.",
                    "help": "Tools for save-state management",
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
                    "description": "Install Ryujinx.",
                    "help": "Install and setup Ryujinx",
                },
                params=[
                    {
                        "dest": "url",
                        "help": "RyujinxKit-content download URL",
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
                    "description": "Create new save state.",
                    "help": "Add to your collection of save states",
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
                    "description": "List save states.",
                    "aliases": ["ls"],
                    "help": "Show all of your save states",
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
                                            ROUND(size / (1024 * 1024.0), 2)
                                            AS TEXT
                                        ) || "MB"
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
                    "description": "Delete one of your save states.",
                    "aliases": ["rm"],
                    "help": "Remove a save state from your collection",
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
                    "description": "Update your save state.",
                    "help": "Update a save state",
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
                    "description": "Restore your save state.",
                    "help": "Restore a save state",
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
                    "description": "Change a save-state's tag.",
                    "help": "Update a save-state's tag",
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
                        "help": "New tag for save state",
                    },
                ],
                parent=Command.RYUJINXKIT_SAVE,
                defaults={
                    "func": sanitize(
                        command=Command.RYUJINXKIT_SAVE_RETAG,
                        function=lambda args: Session.database_cursor.execute(
                            """
                            UPDATE saves
                            SET tag = ?, updated = datetime("now")
                            WHERE id = ?;
                            """,
                            [args.tag, args.id],
                        ),
                    )
                },
            ),
            Command.RYUJINXKIT_SAVE_EXPORT: ParserCommand(
                parser_args={
                    "name": "export",
                    "description": "Export your save states as a .tar file.",
                    "help": "Export your save states",
                    "aliases": ["archive", "x"],
                },
                params=[
                    (
                        ["-o", "--output"],
                        {
                            "help": "Output-file name",
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
                    "description": "Retrieve save states from an export.",
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
    )[1]

    with Session:
        _begin()


# =============================================================================

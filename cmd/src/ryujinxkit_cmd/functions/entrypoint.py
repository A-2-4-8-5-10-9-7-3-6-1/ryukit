"""
Application entrypoint.

Dependency level: 2.
"""

from parser_generator import Command as ParserCommand
from parser_generator import generate
from rich.box import Box
from rich.console import Console
from rich.table import Table

from ..constants.configs import DEFAULT_TAG
from ..constants.configs2 import COLOR_MAP
from ..enums import Command, CustomColor, FileNode, UseOperation
from ..session import Session
from .save_states import create_save, use_save
from .setup import source

# =============================================================================

# prog: str | None = None, usage: str | None = None, description: str | None = None, epilog: str | None = None, parents: Sequence[ArgumentParser] = [], formatter_class: _FormatterClass = ..., prefix_chars: str = "-", fromfile_prefix_chars: str | None = None, argument_default: Any = None, conflict_handler: str = "error", add_help: bool = True, allow_abbrev: bool = True, exit_on_error: bool = True

# (name: str, *, deprecated: bool = False, help: str | None = ..., aliases: Sequence[str] = ..., prog: str | None = ..., usage: str | None = ..., description: str | None = ..., epilog: str | None = ..., parents: Sequence[ArgumentParser] = ..., formatter_class: _FormatterClass = ..., prefix_chars: str = ..., fromfile_prefix_chars: str | None = ..., argument_default: Any = ..., conflict_handler: str = ..., add_help: bool = ..., allow_abbrev: bool = ..., exit_on_error: bool = ..., **kwargs: Any)

# (*name_or_flags: str, action: _ActionStr | type[Action] = ..., nargs: int | _NArgsStr | _SUPPRESS_T | None = None, const: Any = ..., default: Any = ..., type: _ActionType = ..., choices: Iterable[_T@add_argument] | None = ..., required: bool = ..., help: str | None = ..., metavar: str | tuple[str, ...] | None = ..., dest: str | None = ..., version: str = ..., **kwargs: Any)


def entrypoint() -> None:
    """
    Entrypoint function.
    """

    console = Console(color_system="truecolor")
    table = Table(
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
    )
    format_tag = lambda tag: (
        tag.replace(" ", "-").lower() if tag.isalpha() else DEFAULT_TAG
    )

    with Session:
        generate(
            function_attr="func",
            commands={
                Command.ROOT: ParserCommand(
                    parser_args={
                        "prog": "ryujinxkit",
                        "description": "Ryujinx-management toolkit.",
                    },
                    subparsers_args={
                        "title": "operation",
                        "description": "Command operation.",
                        "required": True,
                    },
                    parent=Command.ROOT,
                ),
                Command.SAVE: ParserCommand(
                    parser_args={
                        "name": "save",
                        "description": "Save-state management tools.",
                        "help": "Tools for save-state management.",
                    },
                    subparsers_args={
                        "title": "operation",
                        "description": "Save operation.",
                        "required": True,
                    },
                    parent=Command.ROOT,
                ),
                Command.SOURCE_RYUJINX: ParserCommand(
                    parser_args={
                        "name": "install",
                        "description": "Install Ryujinx.",
                        "help": "Install and setup Ryujinx.",
                    },
                    params=[
                        (
                            [],
                            {
                                "dest": "server_url",
                                "help": "URL for a RyujinxKit server--get "
                                "one from the developer.",
                                "type": str,
                            },
                        )
                    ],
                    parent=Command.ROOT,
                    defaults={
                        "func": lambda args: [
                            source(server_url=args.server_url),
                            console.print(
                                f"[{COLOR_MAP[CustomColor.CREAM]}]App "
                                "installed to: "
                                f"{Session.RESOLVER(id_=FileNode.RYUJINX_APP)}."
                                f"[/{COLOR_MAP[CustomColor.CREAM]}]",
                                highlight=False,
                            ),
                        ]
                    },
                ),
                Command.CREATE_SAVE: ParserCommand(
                    parser_args={
                        "name": "create",
                        "description": "Create new save state.",
                        "help": "Add to your collection of save states.",
                    },
                    params=[
                        (
                            ["-t", "--tag"],
                            {
                                "help": "A tag for your save state.",
                                "type": str,
                            },
                        )
                    ],
                    parent=Command.SAVE,
                    defaults={
                        "func": lambda args: console.print(
                            f"[{COLOR_MAP[CustomColor.CREAM]}]Save ID: "
                            f"{create_save(tag=format_tag(args.tag))}."
                            f"[/{COLOR_MAP[CustomColor.CREAM]}]"
                        ),
                        "tag": DEFAULT_TAG,
                    },
                ),
                Command.LIST_SAVES: ParserCommand(
                    parser_args={
                        "name": "list",
                        "description": "List save states.",
                        "aliases": ["ls"],
                        "help": "Show all of your save states.",
                    },
                    parent=Command.SAVE,
                    defaults={
                        "func": lambda _: [
                            [
                                table.add_row(*map(str, row))
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
                                            ROUND(size / 1000.0, 2)
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
                        ]
                    },
                ),
                Command.REMOVE_SAVE: ParserCommand(
                    parser_args={
                        "name": "remove",
                        "description": "Delete one of your save states.",
                        "aliases": ["rm"],
                        "help": "Remove a save state from your collection.",
                    },
                    params=[
                        (
                            [],
                            {
                                "help": "The save-state's ID.",
                                "type": int,
                                "dest": "id",
                            },
                        )
                    ],
                    parent=Command.SAVE,
                    defaults={
                        "func": lambda args: Session.database_cursor.execute(
                            """
                            DELETE FROM saves
                            WHERE id = ?;
                            """,
                            [args.id],
                        )
                    },
                ),
                Command.USE_SAVE: ParserCommand(
                    parser_args={
                        "name": "use",
                        "description": "Use your save state.",
                        "help": "Use--includes update--a save state.",
                    },
                    params=[
                        (
                            ["-o", "--operation"],
                            {
                                "choices": ["restore", "update"],
                                "help": "Operation to use on save.",
                                "required": True,
                            },
                        ),
                        (
                            [],
                            {
                                "dest": "id",
                                "help": "ID of save state.",
                                "type": str,
                            },
                        ),
                    ],
                    parent=Command.SAVE,
                    defaults={
                        "func": lambda args: use_save(
                            id_=args.id,
                            operation=(
                                UseOperation.RESTORE
                                if args.operation == "restore"
                                else UseOperation.UPDATE
                            ),
                        )
                    },
                ),
                Command.RETAG: ParserCommand(
                    parser_args={
                        "name": "retag",
                        "description": "Change a save-state's tag.",
                        "help": "Update a save-state's tag.",
                    },
                    params=[
                        (
                            ["-t", "--tag"],
                            {
                                "type": str,
                                "required": True,
                                "help": "New tag for save state.",
                            },
                        ),
                        (
                            [],
                            {
                                "dest": "id",
                                "help": "Save-state's ID.",
                                "type": str,
                            },
                        ),
                    ],
                    parent=Command.SAVE,
                    defaults={
                        "func": lambda args: Session.database_cursor.execute(
                            """
                                UPDATE saves
                                SET tag = ?, updated = datetime("now")
                                WHERE id = ?;
                            """,
                            [format_tag(args.tag), args.id],
                        )
                    },
                ),
                Command.ARCHIVE: ParserCommand(
                    parser_args={
                        "name": "archive",
                        "description": "Export your save states as a "
                        "tar file.",
                        "help": "Archive your save states.",
                    },
                    params=[
                        (
                            ["-o", "-output"],
                            {
                                "help": "Name of output file.",
                                "type": str,
                            },
                        )
                    ],
                    parent=Command.SAVE,
                    defaults={
                        "func": lambda _: print("comming soon..."),
                        "output": "save-states.tar",
                    },
                ),
            },
        )[1]()


# =============================================================================

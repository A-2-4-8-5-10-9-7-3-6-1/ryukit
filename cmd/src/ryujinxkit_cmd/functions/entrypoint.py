"""
Application entrypoint.

Dependency level: 2.
"""

from parser_generator import Command as ParserCommand
from parser_generator import generate
from rich.box import Box
from rich.console import Console
from rich.table import Table

from ..constants.configs2 import COLOR_MAP
from ..enums import Command, CustomColor, FileNode
from ..session import Session
from .save_states import create_save
from .setup import source

# =============================================================================

# prog: str | None = None, usage: str | None = None, description: str | None = None, epilog: str | None = None, parents: Sequence[ArgumentParser] = [], formatter_class: _FormatterClass = ..., prefix_chars: str = "-", fromfile_prefix_chars: str | None = None, argument_default: Any = None, conflict_handler: str = "error", add_help: bool = True, allow_abbrev: bool = True, exit_on_error: bool = True

# (name: str, *, deprecated: bool = False, help: str | None = ..., aliases: Sequence[str] = ..., prog: str | None = ..., usage: str | None = ..., description: str | None = ..., epilog: str | None = ..., parents: Sequence[ArgumentParser] = ..., formatter_class: _FormatterClass = ..., prefix_chars: str = ..., fromfile_prefix_chars: str | None = ..., argument_default: Any = ..., conflict_handler: str = ..., add_help: bool = ..., allow_abbrev: bool = ..., exit_on_error: bool = ..., **kwargs: Any)

# (*name_or_flags: str, action: _ActionStr | type[Action] = ..., nargs: int | _NArgsStr | _SUPPRESS_T | None = None, const: Any = ..., default: Any = ..., type: _ActionType = ..., choices: Iterable[_T@add_argument] | None = ..., required: bool = ..., help: str | None = ..., metavar: str | tuple[str, ...] | None = ..., dest: str | None = ..., version: str = ..., **kwargs: Any)


def entrypoint() -> None:
    """
    Entrypoint function.
    """

    console = Console(color_system="truecolor", width=79)
    table = Table(
        "ID",
        "TAG",
        "CREATED",
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
                        "title": "command",
                        "description": "The command to execute.",
                        "required": True,
                    },
                    parent=Command.ROOT,
                ),
                Command.SAVE: ParserCommand(
                    parser_args={
                        "name": "save",
                        "description": "Save-state management tools.",
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
                ),
                Command.CREATE_SAVE: ParserCommand(
                    parser_args={
                        "name": "create",
                        "description": "Create new save state.",
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
                ),
                Command.LIST_SAVES: ParserCommand(
                    parser_args={
                        "name": "list",
                        "description": "List save states.",
                        "aliases": ["ls"],
                    },
                    parent=Command.SAVE,
                ),
            },
            defaults={
                Command.SOURCE_RYUJINX: {
                    "func": lambda args: [
                        source(server_url=args.server_url),
                        console.print(
                            f"[{COLOR_MAP[CustomColor.CREAM]}]App installed "
                            "to: "
                            f"{Session.RESOLVER(id_=FileNode.RYUJINX_APP)}."
                            f"[/{COLOR_MAP[CustomColor.CREAM]}]",
                            highlight=False,
                        ),
                    ]
                },
                Command.CREATE_SAVE: {
                    "func": lambda args: console.print(
                        f"[{COLOR_MAP[CustomColor.CREAM]}]Save ID: "
                        f"{create_save(tag=args.tag)}."
                        f"[/{COLOR_MAP[CustomColor.CREAM]}]"
                    ),
                    "tag": "untagged",
                },
                Command.LIST_SAVES: {
                    "func": lambda _: [
                        [
                            table.add_row(*map(str, row))
                            for row in Session.database_cursor.execute(
                                "SELECT * FROM saves"
                            ).fetchall()
                        ],
                        console.print(table),
                    ]
                },
            },
        )[1]()


# =============================================================================

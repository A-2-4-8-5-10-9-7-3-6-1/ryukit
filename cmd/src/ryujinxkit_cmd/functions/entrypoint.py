"""
Application entrypoint.
"""

from parser_generator import Command as ParserCommand
from parser_generator import generate
from rich.console import Console

from ..enums import Command, FileNode
from ..session import Session
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

    with Session:
        generate(
            function_attr="func",
            commands={
                Command.NULL: ParserCommand(
                    parser_args={
                        "prog": "ryujinxkit",
                        "description": "Ryujinx-management toolkit.",
                    },
                    subparsers_args={
                        "title": "command",
                        "description": "The command to execute.",
                        "required": True,
                    },
                    parent=Command.NULL,
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
                    parent=Command.NULL,
                ),
            },
            defaults={
                Command.SOURCE_RYUJINX: {
                    "func": lambda args: [
                        source(server_url=args.server_url),
                        console.print(
                            "\nInstalled to: "
                            f"{Session.RESOLVER(id_=FileNode.RYUJINX_APP)}.",
                            highlight=False,
                        ),
                    ]
                },
            },
        )[1]()


# =============================================================================

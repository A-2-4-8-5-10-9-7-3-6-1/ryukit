import pathlib
import typing

import typer

from ...services.sqlite3.configs import DB_CONFIGS
from ..commands.save.create.command import create_command
from ..commands.save.delete.command import delete_command
from ..commands.save.export.command import export_command
from ..commands.save.extract.command import extract_command
from ..commands.save.list.command import list_command
from ..commands.save.retag.command import retag_command
from ..commands.save.transfer.command import transfer_command
from ..commands.save.transfer.transfer_op import TransferOp
from .parsers.sort_key import sort_key_parser
from .parsers.tag import tag_parser

save_typer = typer.Typer(invoke_without_command=True)


@save_typer.callback()
def _(
    ctx: typer.Context,
    keys: typing.Annotated[
        list[typing.Any],
        typer.Option(
            "-k",
            "--key",
            metavar="SORT_KEY",
            parser=sort_key_parser,
            help="A sort key.",
        ),
    ] = ["used-", "updated-", "created-", "tag-", "size-"],
) -> None:
    """
    Execute save-related tasks, displaying save instances on a no-arg
    invocation.
    """

    if ctx.invoked_subcommand is None:
        list_command(keys)


@save_typer.command("create")
def _(
    tag: typing.Annotated[
        str,
        typer.Option(
            metavar="TAG",
            help="A tag for your save.",
            parser=tag_parser,
        ),
    ] = DB_CONFIGS["defaults"]["save_tag"]
) -> None:
    """
    Create an empty save.
    """

    create_command(tag)


@save_typer.command(name="remove", epilog="Aliases: rm")
@save_typer.command(name="rm", hidden=True)
def _(
    id_: typing.Annotated[
        str,
        typer.Argument(metavar="ID", help="The save's ID."),
    ]
) -> None:
    """
    Remove a save.
    """

    delete_command(id_)


@save_typer.command(name="operate", epilog="Aliases: op")
@save_typer.command(name="op", hidden=True)
def _(
    operation: typing.Annotated[
        TransferOp,
        typer.Argument(help="Operation to perform."),
    ],
    id_: typing.Annotated[
        str,
        typer.Argument(metavar="ID", help="Save's ID.", case_sensitive=False),
    ],
) -> None:
    """
    Operate on save instances through file transference.
    """

    transfer_command(id_=id_, operation=operation)


@save_typer.command(name="retag", epilog="Aliases: rt")
@save_typer.command(name="rt", hidden=True)
def _(
    id_: typing.Annotated[
        str,
        typer.Argument(metavar="ID", help="Save's ID."),
    ],
    tag: typing.Annotated[
        str,
        typer.Argument(
            metavar="TAG",
            help="Save's new tag.",
            parser=tag_parser,
        ),
    ],
) -> None:
    """
    Change a save's tag.
    """

    retag_command(id_=id_, tag=tag)


@save_typer.command("export")
def _(
    output: typing.Annotated[
        pathlib.Path,
        typer.Option(help="Output-file's path."),
    ] = pathlib.Path("ryujinxkit-saves.tar")
) -> None:
    """
    Export your saves to a tar file.
    """

    export_command(output)


@save_typer.command("extract")
def _(
    path: typing.Annotated[
        pathlib.Path,
        typer.Argument(
            metavar="PATH",
            exists=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to your extract.",
        ),
    ]
) -> None:
    """
    Extract saves from an export.
    """

    extract_command(path)

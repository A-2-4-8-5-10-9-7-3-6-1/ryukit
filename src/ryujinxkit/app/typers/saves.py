import pathlib
import typing

import typer

from ...services.sqlite3.configs import DB_CONFIGS
from ..jobs.save.create.job import create_job
from ..jobs.save.delete.job import delete_job
from ..jobs.save.export.job import export_job
from ..jobs.save.extract.job import extract_job
from ..jobs.save.list.job import list_job
from ..jobs.save.retag.job import retag_job
from ..jobs.save.transfer.job import transfer_job
from ..jobs.save.transfer.transfer_op import TransferOp
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
        list_job(keys)


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

    create_job(tag)


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

    delete_job(id_)


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

    transfer_job(id_=id_, operation=operation)


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

    retag_job(id_=id_, tag=tag)


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

    export_job(output)


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

    extract_job(path)

"""
- dependency level 5.
"""

import pathlib
import typing

import typer

from ..database.configs import SAVE_TAG_DEFAULT
from .jobs.saves.create import job as create_job
from .jobs.saves.delete import job as delete_job
from .jobs.saves.export import job as export_job
from .jobs.saves.extract import job as extract_job
from .jobs.saves.list import job as list_job
from .jobs.saves.retag import job as retag_job
from .jobs.saves.state_transfer import job as transfer_job
from .parsers.sort_key import parser as sort_key_parser
from .parsers.tag import parser as tag_parser

typer_ = typer.Typer(invoke_without_command=True)


@typer_.callback()
def _(
    ctx: typer.Context,
    keys: typing.Annotated[
        list[typing.Any],
        typer.Option(
            "-k",
            "--key",
            parser=sort_key_parser,
            help="A sort key.",
        ),
    ] = ["used-", "updated-", "created-", "tag-", "size-"],
) -> None:
    """
    Execute save-related tasks (displays save instances by default).
    """

    if ctx.invoked_subcommand is None:
        list_job(order=keys)

        raise typer.Exit()


@typer_.command(name="create")
def _(
    tag: typing.Annotated[
        str,
        typer.Option(
            metavar="TAG",
            help="A tag for your save.",
            parser=tag_parser,
        ),
    ] = SAVE_TAG_DEFAULT
) -> None:
    """
    Create an empty save.
    """

    create_job(tag=tag)


@typer_.command(name="remove", epilog="Aliases: rm")
@typer_.command(name="rm", hidden=True)
def _(
    id_: typing.Annotated[
        str,
        typer.Argument(metavar="ID", help="The save's ID."),
    ]
) -> None:
    """
    Remove a save.
    """

    delete_job(id_=id_)


@typer_.command(name="update")
def _(
    id_: typing.Annotated[
        str,
        typer.Argument(metavar="ID", help="Save's ID."),
    ]
) -> None:
    """
    Copy Ryujinx environment into a save.
    """

    transfer_job(id_=id_, operation="update")


@typer_.command(name="restore")
def _(
    id_: typing.Annotated[str, typer.Argument(metavar="ID", help="Save's ID.")]
) -> None:
    """
    Restore your Ryujinx environment from save.
    """

    transfer_job(id_=id_, operation="restore")


@typer_.command(name="retag", epilog="Aliases: rt")
@typer_.command(name="rt", hidden=True)
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


@typer_.command(name="export")
def _(
    output: typing.Annotated[
        pathlib.Path,
        typer.Option(help="Output-file's path."),
    ] = pathlib.Path("ryujinxkit-saves.tar")
) -> None:
    """
    Export your saves to a tar file.
    """

    export_job(output=output)


@typer_.command(name="extract")
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

    extract_job(path=path)

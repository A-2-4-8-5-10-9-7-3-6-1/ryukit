"""
- dependency level 6.
"""

import typing

import typer

from .info_callback.decorator import decorator as info_callback
from .jobs.app.author import job as author_job
from .jobs.app.version import job as version_job
from .jobs.ryujinx.install import job as install_job
from .saves import typer_ as save_typer

typer_ = typer.Typer(
    name="ryujinxkit",
    rich_markup_mode=None,
    invoke_without_command=True,
)

typer_.add_typer(typer_instance=save_typer, name="save", epilog="Aliases: sv")
typer_.add_typer(typer_instance=save_typer, name="sv", hidden=True)


@typer_.callback()
def _(
    ctx: typer.Context,
    url: typing.Annotated[
        str,
        typer.Option(
            metavar="URL",
            help="Download URL (aquired from an authority).",
            envvar="RYUJINXKIT_SERVICE_URL",
        ),
    ],
    version: typing.Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show version and quit.",
            callback=info_callback(job=version_job),
        ),
    ] = False,
    author: typing.Annotated[
        bool,
        typer.Option(
            "--author",
            help="Show author and quit.",
            callback=info_callback(job=author_job),
        ),
    ] = False,
) -> None:
    """
    CLI for Ryujinx (Windows) management (installs Ryujinx by default).
    """

    if ctx.invoked_subcommand is None:
        install_job(url=url)

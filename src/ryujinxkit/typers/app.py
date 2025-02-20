import collections
import collections.abc
import typing

import typer

from .context.settings import settings
from .helpers.decorators.info_callback import decorator as info_callback
from .jobs.author import job as author_job
from .jobs.install import job as install_job
from .jobs.version import job as version_job
from .saves import typer_ as save_typer

typer_ = typer.Typer(
    name="ryujinxkit",
    rich_markup_mode=None,
    invoke_without_command=True,
)

typer_.add_typer(typer_instance=save_typer, name="save", epilog="Aliases: sv")
typer_.add_typer(typer_instance=save_typer, name="sv", hidden=True)


def _update_context(
    setting: str,
) -> collections.abc.Callable[[typing.Any], None]:
    def inner(arg: typing.Any) -> None:
        settings[setting] = arg

    return inner


@typer_.callback()
def _(
    ctx: typer.Context,
    url: typing.Annotated[
        str,
        typer.Option(
            metavar="URL",
            help="Download URL (aquired from an authority).",
            envvar="RYUJINXKIT_SERVICE",
        ),
    ],
    version: typing.Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show version and quit.",
            callback=info_callback(version_job),
        ),
    ] = False,
    json: typing.Annotated[
        bool,
        typer.Option(
            "--json",
            help="Enable JSON output.",
            callback=_update_context("json"),
        ),
    ] = settings["json"],
    author: typing.Annotated[
        bool,
        typer.Option(
            "--author",
            help="Show author and quit.",
            callback=info_callback(author_job),
        ),
    ] = False,
) -> None:
    """
    CLI for Ryujinx (Windows) management (installs Ryujinx by default).
    """

    if ctx.invoked_subcommand is None:
        install_job(url)

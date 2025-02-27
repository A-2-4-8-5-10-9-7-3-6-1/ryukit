import collections
import collections.abc
import importlib
import importlib.metadata
import typing

import typer

from ...core.ui.configs import UI_CONFIGS
from ..commands.info.author.command import author_command
from ..commands.info.version.command import version_command
from ..commands.other.install.command import install_command
from ..context import settings
from .decorators.info_callback import info_callback_decorator
from .saves import save_typer

app_typer = typer.Typer(
    name="ryujinxkit",
    invoke_without_command=True,
    help=f"{importlib.metadata.metadata("ryujinxkit")["summary"]}"
    " Invoke without argument to install Ryujinx.",
    **UI_CONFIGS["typer_settings"],
)

app_typer.add_typer(
    typer_instance=save_typer,
    name="save",
    epilog="Aliases: sv",
)
app_typer.add_typer(typer_instance=save_typer, name="sv", hidden=True)


def _update_context(
    setting: str,
) -> collections.abc.Callable[[typing.Any], None]:
    """
    Get a function that modifies a context setting.

    :param setting: The setting to modify.

    :returns: A function for modifying the given setting.
    """

    def inner(arg: typing.Any) -> None:
        settings[setting] = arg

    return inner


@app_typer.callback()
def _(
    ctx: typer.Context,
    url: typing.Annotated[
        str,
        typer.Option(
            metavar="URL",
            help="Download URL (aquired from an authority).",
            envvar="RYUJINXKIT_SERVICE",
        ),
    ] = "",
    version: typing.Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show version and quit.",
            callback=info_callback_decorator(version_command),
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
            callback=info_callback_decorator(author_command),
        ),
    ] = False,
) -> None:
    if not ctx.invoked_subcommand:
        install_command(url)

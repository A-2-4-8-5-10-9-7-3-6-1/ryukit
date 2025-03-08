import importlib
import importlib.metadata
import typing

import typer

from ...core.ui.configs import UI_CONFIGS
from ..commands.info.author import author_command
from ..commands.info.version import version_command
from ..commands.misc.install import install_command
from ..context import settings
from .saves import save_typer

__all__ = ["app_typer"]
app_typer = typer.Typer(
    name="ryujinxkit",
    invoke_without_command=True,
    help=f"{importlib.metadata.metadata("ryujinxkit")["summary"]}"
    " Invoke without argument to install Ryujinx.",
    **UI_CONFIGS["typer_settings"],
)

app_typer.add_typer(
    typer_instance=save_typer, name="save", epilog="Aliases: sv"
)
app_typer.add_typer(typer_instance=save_typer, name="sv", hidden=True)


@app_typer.callback()
def _(
    url: typing.Annotated[
        str | None,
        typer.Option(
            metavar="URL",
            help="Download URL (aquired from an authority).",
            envvar="RYUJINXKIT_SERVICE",
        ),
    ] = None,
    version: typing.Annotated[
        bool, typer.Option("--version", help="Show version and quit.")
    ] = False,
    json: typing.Annotated[
        bool, typer.Option("--json", help="Enable JSON output.")
    ] = settings["json"],
    author: typing.Annotated[
        bool, typer.Option("--author", help="Show author and quit.")
    ] = False,
) -> None:
    settings["json"] = json

    for command, use in [(version_command, version), (author_command, author)]:
        if not use:
            continue

        command()

        raise typer.Exit

    if url:
        install_command(url)

        raise typer.Exit

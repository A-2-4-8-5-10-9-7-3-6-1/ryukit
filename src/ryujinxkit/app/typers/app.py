"""Defines the root typer.

Exports
-------
- :func:`app_typer`: Root typer.
"""

import importlib
import importlib.metadata
import typing

import typer

from ...core.ui.styling import styled
from ..commands.misc.info import InfoCommandSubject, info_command
from ..commands.misc.install import install_command
from ..context import settings
from .save import save_typer

app_typer = styled(typer.Typer)(
    name="ryujinxkit",
    invoke_without_command=True,
    help=f"{importlib.metadata.metadata("ryujinxkit")["summary"]}"
    " Invoke without argument to install Ryujinx.",
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

    for subject, use in [
        (InfoCommandSubject.VERSION, version),
        (InfoCommandSubject.AUTHOR, author),
    ]:
        if not use:
            continue

        info_command(subject)

        raise typer.Exit

    if url:
        install_command(url)

        raise typer.Exit

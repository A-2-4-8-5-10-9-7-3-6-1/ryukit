"""
- dependency level 2.
"""

import typing

import requests
import typer

import ryujinxkit.data
import ryujinxkit.general

from ..objects import Objects
from .save import save

app = typer.Typer(name="ryujinxkit", rich_markup_mode=None)

app.add_typer(typer_instance=save, name="save", epilog="Aliases: sv")
app.add_typer(typer_instance=save, name="sv", hidden=True)


def _version_callback() -> None:
    """
    Show version and quit.
    """

    Objects.console.print(
        f"RyujinxKit version {ryujinxkit.general.APP_VERSION}."
    )

    raise typer.Exit()


@app.callback()
def _(
    _: typing.Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show version and quit.",
            callback=lambda x: _version_callback() if x else None,
        ),
    ] = False,
) -> None:
    """
    CLI for Ryujinx (Windows) management.
    """


@app.command(name="install", epilog="Aliases: i")
@app.command(name="i", hidden=True)
def _(
    url: typing.Annotated[
        str,
        typer.Argument(
            metavar="URL",
            help="Download URL (aquired from an authority).",
            envvar="RYUJINXKIT_SERVICE_URL",
        ),
    ]
) -> None:
    """
    Install and ready Ryujinx.
    """

    try:
        ryujinxkit.data.source(console=Objects.console, url=url)

        Objects.console.print(
            f"Installed to {
                ryujinxkit.general.Session.resolver(
                    id_=ryujinxkit.general.FileNode.RYUJINX_LOCAL_DATA
                )
            }.",
        )

    except requests.ConnectionError:
        Objects.console.print("Failed to connect to service.")

    except Exception:
        Objects.console.print(
            "An error occured. This was the resullt of one of the "
            "following:\n",
            "(1) Your URL locates an invalid service,",
            "(2) Your connection timed out.",
            "\nIn case of (1), contact an authority for a valid URL.",
            sep="\n",
        )

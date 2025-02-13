"""
- dependency level 1.
"""

from typing import Annotated

from requests import ConnectionError
from typer import Argument, Exit, Option, Typer

from ryujinxkit.data import source
from ryujinxkit.general import APP_VERSION, FileNode, Session

from .save import save_commands

# =============================================================================

_app = Typer(name="ryujinxkit", rich_markup_mode=None)

# -----------------------------------------------------------------------------

_app.add_typer(typer_instance=save_commands, name="save", epilog="Aliases: sv")
_app.add_typer(typer_instance=save_commands, name="sv", hidden=True)

# -----------------------------------------------------------------------------


def main() -> None:
    """
    Entry-point.
    """

    try:
        with Session:
            _app()

    except BaseException:
        pass


# -----------------------------------------------------------------------------


def _version_callback() -> None:
    """
    Show version and quit.
    """

    Session.console.print(f"RyujinxKit version {APP_VERSION}.")

    raise Exit()


# -----------------------------------------------------------------------------


@_app.callback()
def _(
    _: Annotated[
        bool,
        Option(
            "--version",
            help="Show version and quit.",
            callback=lambda x: _version_callback() if x else None,
        ),
    ] = False,
) -> None:
    """
    CLI for Ryujinx (Windows) management.
    """


# -----------------------------------------------------------------------------


@_app.command(name="install", epilog="Aliases: i")
@_app.command(name="i", hidden=True)
def _(
    url: Annotated[
        str,
        Argument(
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
        source(console=Session.console, url=url)

        Session.console.print(
            f"Installed to {
                Session.resolver(id_=FileNode.RYUJINX_LOCAL_DATA)
            }.",
        )

    except ConnectionError:
        Session.console.print("Failed to connect to service.")

    except Exception:
        Session.console.print(
            "An error occured. This was the resullt of one of the "
            "following:\n",
            "(1) Your URL locates an invalid service,",
            "(2) Your connection timed out.",
            "\nIn case of (1), contact an authority for a valid URL.",
            sep="\n",
        )


# =============================================================================

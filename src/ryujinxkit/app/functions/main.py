"""
- dependency level 1.
"""

from typing import Annotated

from requests import ConnectionError
from typer import Exit, Option, Typer

from ryujinxkit.data import source
from ryujinxkit.general import APP_VERSION, FileNode, Session

from .save_commands import save_commands

# =============================================================================

_app = Typer(name="ryujinxkit", rich_markup_mode=None)

# -----------------------------------------------------------------------------

_app.add_typer(typer_instance=save_commands)

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


@_app.callback(invoke_without_command=True)
def _(
    version: Annotated[
        bool,
        Option("--version", help="Show version and quit."),
    ] = False,
) -> None:
    """
    CLI for Ryujinx (Windows) management.
    """

    if version:
        Session.console.print(f"RyujinxKit version {APP_VERSION}.")

        raise Exit()


# -----------------------------------------------------------------------------


@_app.command(name="install")
def _(
    url: Annotated[
        str,
        Option(
            help="Download URL (aquired from an authority)",
            envvar="RYUJINXKIT_SERVICE_URL",
        ),
    ]
) -> None:
    """
    Install and ready Ryujinx.
    """

    try:
        source(Session.console, url=url)

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

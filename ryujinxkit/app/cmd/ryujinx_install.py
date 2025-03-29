import typer

from ...core import ui
from ..modules import context

__all__ = []


@context.root_typer.command("ryujinx-install")
def _():
    """
    Install Ryujinx from your configured source.

    INSTRUCTIONS
    ------------

    Before using this command, set 'ryujinxInstallURL' in ryujinxkit-config.json.
    """

    if not context.states.configs["ryujinxInstallURL"]:
        ui.app_console.print(
            "[error]Command cannot be used without setting 'ryujinxInstallURL'. Use '--help' for more information."
        )

        raise typer.Exit(1)

    ...

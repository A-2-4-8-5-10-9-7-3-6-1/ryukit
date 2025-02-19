from ....display.console import console
from ...context.settings import settings
from .enums.commands import Enum as Command
from .typing.presenter import Presenter


def present() -> Presenter[bool]:
    """
    Present information from the delete command.
    """

    signal = yield

    if isinstance(signal, Command):
        return

    if settings["json"]:
        return console.print_json(
            data={
                "success": signal,
            }
        )

    if signal:
        return console.print("Save deleted.")

    console.print("Unrecognized save ID.")

from ....display.console import console
from ...context.settings import settings
from .enums.commands import Enum as Command
from .typing.presenter import Presenter


def present() -> Presenter[int]:
    """
    Present information from the extract action.
    """

    signal = yield

    if isinstance(signal, Command):
        return

    if settings["json"]:
        return console.print_json(
            data={
                "id": signal,
            }
        )

    console.print(f"ID: {signal}.")

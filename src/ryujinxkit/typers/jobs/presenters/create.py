from ....display.console import console
from ...context.settings import settings
from ..messages.primers import Primer
from .types.presenter import Presenter


def present() -> Presenter[int]:
    """
    Present information from the extract action.
    """

    signal = yield

    if isinstance(signal, Primer):
        return

    if settings["json"]:
        return console.print_json(
            data={
                "id": signal,
            }
        )

    console.print(f"ID: {signal}.")

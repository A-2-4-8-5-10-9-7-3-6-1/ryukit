from ....display.console import console
from ...context.settings import settings
from ..messages.primers import Primer
from .types.presenter import Presenter


def present() -> Presenter[str]:
    signal = yield

    if isinstance(signal, Primer):
        return

    if settings["json"]:
        return console.print_json(
            data={
                "author": signal,
            }
        )

    console.print(f"{signal} @ https://github.com/{signal}")

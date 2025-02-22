from .....libs.jobs.annotations import Presenter
from .....libs.jobs.signals import Primer
from .....libs.ui.console import console
from ....context import settings


def presenter() -> Presenter[int]:
    signal = yield

    if isinstance(signal, Primer):
        return

    if settings["json"]:
        return console.print_json(
            data={
                "success": signal,
            }
        )

    if signal:
        return console.print("Tag updated.")

    console.print("Unrecognized save ID.")

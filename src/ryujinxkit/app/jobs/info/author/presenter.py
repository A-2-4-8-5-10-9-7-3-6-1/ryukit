from .....libs.jobs.annotations import Presenter
from .....libs.jobs.signals import Primer
from .....libs.ui.console import console
from ....context import settings


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

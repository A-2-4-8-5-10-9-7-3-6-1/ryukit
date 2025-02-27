from .....core.ui.console import console
from ....context import settings
from ...annotations import Presenter
from ...signals import Primer


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

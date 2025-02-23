from .....core.ui.console import console
from ....context import settings
from ...annotations import Presenter
from ...signals import Primer


def presenter() -> Presenter[int]:
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

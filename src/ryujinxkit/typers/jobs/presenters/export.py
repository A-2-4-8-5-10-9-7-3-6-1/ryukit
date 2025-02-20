from ....display.configs import UI_REFRESH_RATE
from ....display.console import console
from .types.presenter import Presenter


def present() -> Presenter[None]:
    with console.status(
        status="[dim]Exporting",
        spinner_style="dim",
        refresh_per_second=UI_REFRESH_RATE,
    ):
        yield

    console.print("Export completed.")

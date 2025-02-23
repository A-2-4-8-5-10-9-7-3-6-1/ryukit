from .....core.ui.configs import UI_CONFIGS
from .....core.ui.console import console
from ...annotations import Presenter


def presenter() -> Presenter[None]:
    with console.status(
        status="[dim]Exporting",
        spinner_style="dim",
        refresh_per_second=UI_CONFIGS["refresh_rate"],
    ):
        yield

    console.print("Export completed.")

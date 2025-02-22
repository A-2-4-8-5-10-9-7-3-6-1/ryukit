from .....libs.jobs.annotations import Presenter
from .....libs.ui.configs import UI_CONFIGS
from .....libs.ui.console import console


def presenter() -> Presenter[None]:
    with console.status(
        status="[dim]Exporting",
        spinner_style="dim",
        refresh_per_second=UI_CONFIGS["refresh_rate"],
    ):
        yield

    console.print("Export completed.")

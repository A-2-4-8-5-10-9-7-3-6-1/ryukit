import typing

import rich.progress
import rich.status

from .....libs.fs.node import Node
from .....libs.fs.resolver import resolver
from .....libs.jobs.annotations import Presenter
from .....libs.jobs.signals import Primer
from .....libs.ui.configs import UI_CONFIGS
from .....libs.ui.console import console
from ....context import settings
from .signals import InstallSignal


def present() -> Presenter[tuple[InstallSignal, float]]:
    looping = False
    animation: rich.progress.Progress | rich.status.Status | None = None
    task_id: rich.progress.TaskID | None = None

    while True:
        match (yield):
            case InstallSignal.SERVICE_CONNECT, _:
                animation = console.status(
                    status="[dim]Connecting to service",
                    spinner_style="dim",
                )

                animation.start()

            case InstallSignal.FAILED, 0:
                looping = False

                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={
                            "code": "SERVICE_CONNECTION_ISSUE",
                        }
                    )

                return console.print("Failed to connect to service.")

            case InstallSignal.DOWNLOADING, volume:
                if looping:
                    typing.cast(rich.progress.Progress, animation).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                typing.cast(rich.status.Status, animation).stop()

                animation = rich.progress.Progress(
                    rich.progress.SpinnerColumn(style="dim"),
                    "[dim]{task.description}",
                    "[dim]({task.percentage:.1f}%)",
                    console=console,
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
                    transient=True,
                )
                task_id = animation.add_task(
                    description="Downloading",
                    total=volume,
                )
                looping = True

                animation.start()

            case InstallSignal.UNPACKING, volume:
                typing.cast(rich.progress.Progress, animation).stop()

                looping = False
                animation = console.status(
                    status="[dim]Unpacking",
                    spinner_style="dim",
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
                )

                animation.start()

            case InstallSignal.FAILED, 1:
                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={
                            "code": "NETWORK_ISSUE",
                        }
                    )

                return console.print(
                    "An error occured. This was the resullt of one of the "
                    "following:\n",
                    "(1) Your URL locates an invalid service,",
                    "(2) Your connection timed out.",
                    "\nIn case of (1), contact an authority for a valid URL.",
                    sep="\n",
                )

            case Primer.FINISHED:
                looping = False

                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={
                            "code": "SUCCESS",
                            "path": str(resolver[Node.RYUJINX_LOCAL_DATA]),
                        }
                    )

                return console.print(
                    f"Ryujinx installed to {
                        resolver[Node.RYUJINX_LOCAL_DATA]
                    }."
                )

            case Primer.KILL:
                if animation is not None:
                    animation.stop()

                return

            case _:
                pass

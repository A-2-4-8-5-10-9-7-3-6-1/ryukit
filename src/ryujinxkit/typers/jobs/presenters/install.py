import typing

import rich.progress
import rich.status

from ....display.configs import UI_REFRESH_RATE
from ....display.console import console
from ....file_access.resolver import resolver
from ....file_access.resolver_node import ResolverNode
from ...context.settings import settings
from ..messages.install import InstallSignal
from ..messages.primers import Primer
from .types.presenter import Presenter


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
                    refresh_per_second=UI_REFRESH_RATE,
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
                    refresh_per_second=UI_REFRESH_RATE,
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
                            "path": str(
                                resolver[ResolverNode.RYUJINX_LOCAL_DATA]
                            ),
                        }
                    )

                return console.print(
                    f"Ryujinx installed to {
                        resolver[ResolverNode.RYUJINX_LOCAL_DATA]
                    }."
                )

            case Primer.KILL:
                if animation is not None:
                    animation.stop()

                return

            case _:
                pass

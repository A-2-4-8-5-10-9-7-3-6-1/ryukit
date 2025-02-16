"""
- dependency level 2.
"""

import collections.abc

import rich.progress

from ....file_access.resolver import resolver
from ....file_access.resolver_node import ResolverNode
from .animation.protocol import Protocol as Animation
from .display.configs import UI_REFRESH_RATE
from .display.console import console


def present() -> collections.abc.Generator[None, tuple[str, float]]:
    """
    Present information from Ryujinx-install action.
    """

    looping: bool = False
    animation: Animation
    task_id: rich.progress.TaskID

    while True:
        match (yield):
            case "SERVICE_CONNECT", _:
                animation = console.status(
                    status="[dim]Connecting to service",
                    spinner_style="dim",
                )

                animation.start()

            case "FAILED", 0:
                looping = False

                animation.stop()  # type: ignore

                return console.print("Failed to connect to service.")

            case "DOWNLOADING", volume:
                if not looping:
                    animation.stop()  # type: ignore

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

                    continue

                animation.advance(task_id=task_id, advance=volume)  # type: ignore

            case "UNPACKING", volume:
                looping = False

                animation.stop()  # type: ignore

                animation = console.status(
                    status="[dim]Unpacking",
                    spinner_style="dim",
                    refresh_per_second=UI_REFRESH_RATE,
                )

                animation.start()

            case "FAILED", 1:
                animation.stop()  # type: ignore

                return console.print(
                    "An error occured. This was the resullt of one of the "
                    "following:\n",
                    "(1) Your URL locates an invalid service,",
                    "(2) Your connection timed out.",
                    "\nIn case of (1), contact an authority for a valid URL.",
                    sep="\n",
                )

            case "FINISHED", -1:
                looping = False

                animation.stop()  # type: ignore

                return console.print(
                    f"Ryujinx installed to {
                        resolver[ResolverNode.RYUJINX_LOCAL_DATA]
                    }."
                )

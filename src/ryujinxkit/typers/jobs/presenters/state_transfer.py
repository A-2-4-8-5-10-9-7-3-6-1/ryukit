"""
- dependency level 1.
"""

import collections.abc

import rich.progress

from .animation.protocol import Protocol as Animation
from .display.configs import UI_REFRESH_RATE
from .display.console import console


def present() -> collections.abc.Generator[None, tuple[str, float]]:
    """
    Present information from save-transfer actions.
    """

    looping: bool = False
    animation: Animation
    task_id: rich.progress.TaskID

    while True:
        match (yield):
            case "FAILED", 0:
                return console.print("Unrecognized save ID.")

            case "TRANSFERING", volume:
                if looping:
                    animation.advance(task_id=task_id, advance=volume)  # type: ignore

                    continue

                animation = rich.progress.Progress(
                    rich.progress.SpinnerColumn(style="dim"),
                    "[dim]{task.description}",
                    "[dim]({task.completed}/{task.total})",
                    console=console,
                    refresh_per_second=UI_REFRESH_RATE,
                    transient=True,
                )
                task_id = animation.add_task(
                    description="Transfering",
                    total=volume,
                )
                looping = True

                animation.start()

            case "FINISHED", -1:
                looping = False

                animation.stop()  # type: ignore

                return console.print("Transfer successful.")

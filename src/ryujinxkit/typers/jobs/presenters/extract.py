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
    Present information from the extract command.
    """

    looping: bool = False
    animation: Animation
    task_id: rich.progress.TaskID
    r_total: float

    while True:
        match (yield):
            case "EXTRACTING", _:
                animation = console.status(
                    status="Extracting",
                    spinner_style="dim",
                    refresh_per_second=UI_REFRESH_RATE,
                )

                animation.start()

            case "FAILED", 0:
                looping = False

                animation.stop()  # type: ignore

                return console.print("Malformed export file.")

            case "READING", volume:
                if looping:
                    animation.advance(task_id=task_id, advance=volume)  # type: ignore

                    continue

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
                    description="Reading", total=volume
                )
                r_total = volume
                looping = True

                animation.start()

            case "FINISHED", -1:
                looping = False

                animation.stop()  # type: ignore

                return console.print(f"Accepted {r_total} save instance(s).")  # type: ignore

"""
- dependency level 1.
"""

import collections.abc

import rich.progress

from .display.configs import UI_REFRESH_RATE
from .display.console import console


def present() -> collections.abc.Generator[None, tuple[str, float]]:
    """
    Present information from the extract command.
    """

    reading_total: float

    if (yield)[1] == -1:
        console.print("Malformed export file.")

        yield

    with console.status(
        status="Extracting",
        spinner_style="dim",
        refresh_per_second=UI_REFRESH_RATE,
    ):
        reading_total = (yield)[1]

    if reading_total == -1:
        console.print("Malformed export file.")

        yield

    with rich.progress.Progress(
        rich.progress.SpinnerColumn(style="dim"),
        "[dim]{task.description}",
        "[dim]({task.percentage:.1f}%)",
        console=console,
        refresh_per_second=UI_REFRESH_RATE,
        transient=True,
    ) as progress:
        task_id = progress.add_task(description="Reading", total=reading_total)

        while True:
            volume = (yield)[1]

            if volume == -1:
                console.print("Malformed export file.")

                yield

            progress.advance(task_id=task_id, advance=volume)

    console.print(f"Accepted {reading_total} save instance(s).")

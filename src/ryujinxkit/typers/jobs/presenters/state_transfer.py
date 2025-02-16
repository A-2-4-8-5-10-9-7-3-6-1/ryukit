"""
- dependency level 1.
"""

import collections.abc

import rich.progress

from .display.configs import UI_REFRESH_RATE
from .display.console import console


def present() -> collections.abc.Generator[None, tuple[str, float]]:
    """
    Present information from save-transfer actions.
    """

    volume = (yield)[1]

    if volume == -1:
        console.print("Unrecognized save ID.")

        yield

    with rich.progress.Progress(
        rich.progress.SpinnerColumn(style="dim"),
        "[dim]{task.description}",
        "[dim]({task.completed}/{task.total})",
        console=console,
        refresh_per_second=UI_REFRESH_RATE,
        transient=True,
    ) as progress:
        task_id = progress.add_task(description="Transfering", total=volume)

        while True:
            progress.advance(task_id=task_id, advance=(yield)[1])

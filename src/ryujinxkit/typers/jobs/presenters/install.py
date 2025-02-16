"""
- dependency level 1.
"""

import collections.abc

import rich.progress

from .display.configs import UI_REFRESH_RATE
from .display.console import console


def present() -> collections.abc.Generator[None, tuple[str, float]]:
    """
    Present information from Ryujinx-install action.
    """

    download_total: float

    yield

    with console.status(
        status="[dim]Connecting to service",
        spinner_style="dim",
    ):
        download_total = (yield)[1]

    if download_total == -1:
        console.print("Failed to connect to service.")

    with rich.progress.Progress(
        rich.progress.SpinnerColumn(style="dim"),
        "[dim]{task.description}",
        "[dim]({task.percentage:.1f}%)",
        console=console,
        refresh_per_second=UI_REFRESH_RATE,
        transient=True,
    ) as progress:
        task_id = progress.add_task(
            description="Downloading",
            total=download_total,
        )
        status: str | None = None

        while status in {"DOWNLOADING", None}:
            status, size = yield

            progress.advance(task_id=task_id, advance=size)

    with console.status(
        status="[dim]Unpacking",
        spinner_style="dim",
        refresh_per_second=UI_REFRESH_RATE,
    ):
        if (yield)[1] == -1:
            console.print(
                "An error occured. This was the resullt of one of the "
                "following:\n",
                "(1) Your URL locates an invalid service,",
                "(2) Your connection timed out.",
                "\nIn case of (1), contact an authority for a valid URL.",
                sep="\n",
            )

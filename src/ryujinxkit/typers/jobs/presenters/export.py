"""
- dependency level 1.
"""

import collections.abc

from .display.configs import UI_REFRESH_RATE
from .display.console import console


def present() -> collections.abc.Generator[None]:
    """
    Present information from the extract action.
    """

    with console.status(
        status="[dim]Exporting",
        spinner_style="dim",
        refresh_per_second=UI_REFRESH_RATE,
    ):
        yield

    console.print("Export completed.")

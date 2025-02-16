"""
- dependency level 1.
"""

import collections.abc

from .display.console import console


def present() -> collections.abc.Generator[None, int]:
    """
    Present information from the delete command.
    """

    if (yield):
        console.print("Tag updated.")

        yield

    console.print("Unrecognized save ID.")

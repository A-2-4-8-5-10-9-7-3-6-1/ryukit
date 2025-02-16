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
        return console.print("Tag updated.")

    console.print("Unrecognized save ID.")

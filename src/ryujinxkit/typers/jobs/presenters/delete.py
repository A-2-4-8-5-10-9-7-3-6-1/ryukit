"""
- dependency level 1.
"""

import collections.abc

from .display.console import console


def present() -> collections.abc.Generator[None, bool]:
    """
    Present information from the delete command.
    """

    if (yield):
        console.print("Save deleted.")

        yield

    console.print("Unrecognized save ID.")

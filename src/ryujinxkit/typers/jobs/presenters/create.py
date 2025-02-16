"""
- dependency level 1.
"""

import collections.abc

from .display.console import console


def present() -> collections.abc.Generator[None, int]:
    """
    Present information from the extract action.
    """

    console.print(f"ID: {(yield)}.")

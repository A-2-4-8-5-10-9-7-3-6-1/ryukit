"""
- dependency level 1.
"""

import collections
import collections.abc

from .display.console import console


def present() -> collections.abc.Generator[None, str]:
    """
    Present information from the author action.
    """

    console.print((yield))

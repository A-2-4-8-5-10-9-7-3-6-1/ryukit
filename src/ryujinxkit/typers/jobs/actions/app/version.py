"""
- dependency level 1.
"""

from .....metadata import VERSION


def action() -> str:
    """
    Get app's version.

    :returns: App's version.
    """

    return VERSION

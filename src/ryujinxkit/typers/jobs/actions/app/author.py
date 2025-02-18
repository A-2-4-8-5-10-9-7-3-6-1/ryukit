"""
- dependency level 0.
"""

from .....metadata import AUTHOR


def action() -> str:
    """
    Get app's author.

    :returns: App's author.
    """

    return f"https://github.com/{AUTHOR}"

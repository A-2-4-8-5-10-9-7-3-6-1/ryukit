"""
- dependency level 0.
"""

from .....configs import APP_AUTHOR


def action() -> str:
    """
    Get app's author.

    :returns: App's author.
    """

    return f"https://github.com/{APP_AUTHOR}"

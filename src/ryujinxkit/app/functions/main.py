"""
- dependency level 3.
"""

import ryujinxkit.data
import ryujinxkit.general

from ..typers.app import app


def main() -> None:
    """
    Entry-point.
    """

    try:
        with ryujinxkit.general.Session:
            app()

    except BaseException:
        pass

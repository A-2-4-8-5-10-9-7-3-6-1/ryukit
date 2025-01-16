"""
Application entrypoint.
"""

from os import getenv

from ..session import Session
from .setup import source

# =============================================================================


def entrypoint() -> None:
    """
    Entrypoint function.
    """

    with Session:
        source(server_url=getenv(key="DOWNLOAD_LINK"))


# =============================================================================

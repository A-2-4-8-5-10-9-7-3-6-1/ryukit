"""
- dependency level 1.
"""

from logging import INFO, basicConfig, getLogger
from typing import Any

from .constants.configs import RYUJINXKIT_SERVER_NAME

# =============================================================================


class _Meta(type):
    """
    `Session` metaclass.
    """

    def __enter__(cls) -> None:
        """
        Start session.
        """

        basicConfig(level=INFO, format="%(asctime)s - %(message)s")

    # -------------------------------------------------------------------------

    def __exit__(cls, *_: Any) -> None:
        """
        Close session.
        """


# -----------------------------------------------------------------------------


class Session(metaclass=_Meta):
    """
    Session-management class.

    :attr LOGGER: Session's logger.
    """

    LOGGER = getLogger(name=RYUJINXKIT_SERVER_NAME)

    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        raise NotImplementedError


# =============================================================================

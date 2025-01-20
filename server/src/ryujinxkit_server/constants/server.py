"""
Flask related constants.

Dependency level: 1.
"""

from pathlib import Path

from flask import Flask

from .configs import CONTENT_PATH, SERVER_NAME

# =============================================================================

APP = Flask(import_name=SERVER_NAME)

# -----------------------------------------------------------------------------


@APP.route(rule="/")
def _() -> bytes:
    """
    Route to get server content.

    :returns: Content pack as bytes.
    """

    return Path(CONTENT_PATH).read_bytes()


# =============================================================================

"""
Flask related constants.

Dependency level: 1.
"""

from pathlib import Path

from flask import Flask, Response, request

from .configs import CONTENT_PATH, SERVER_NAME
from .logging import LOGGER

# =============================================================================

APP = Flask(import_name=SERVER_NAME)

# -----------------------------------------------------------------------------


@APP.before_request
def _() -> None:
    """
    Log request to console.
    """

    LOGGER.info(
        msg=f"Client {request.remote_addr} requested {request.method} "
        f"{request.path} {request.remote_addr}."
    )


# -----------------------------------------------------------------------------


@APP.route(rule="/")
def _() -> bytes:
    """
    Route to get server content.

    :returns: Content pack as bytes.
    """

    return Path(CONTENT_PATH).read_bytes()


# -----------------------------------------------------------------------------


@APP.after_request
def _(response: Response) -> Response:
    """
    Log connection completion.

    :param response: Response from connection protocol.

    :returns: `response` unaltered.
    """

    LOGGER.info(
        msg=f"Closed connection with {request.remote_addr}. "
        f"Status: {response.status_code}."
    )

    return response


# =============================================================================

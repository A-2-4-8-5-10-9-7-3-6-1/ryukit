"""
- dependency level 2.
"""

from pathlib import Path

from flask import Flask, Response, request

from ..session import Session
from .configs import RYUJINX_CONTENT, RYUJINXKIT_SERVER_NAME

# =============================================================================

SERVER = Flask(import_name=RYUJINXKIT_SERVER_NAME)

# -----------------------------------------------------------------------------


@SERVER.before_request
def _() -> None:
    """
    Log request to console.
    """

    Session.LOGGER.info(
        msg=f"Client {request.remote_addr} requested {request.method} "
        f"{request.path} {request.remote_addr}."
    )


# -----------------------------------------------------------------------------


@SERVER.route(rule="/")
def _() -> bytes:
    """
    Route to get server content.

    :returns: Content pack as bytes.
    """

    return Path(RYUJINX_CONTENT).read_bytes()


# -----------------------------------------------------------------------------


@SERVER.after_request
def _(response: Response) -> Response:
    """
    Log connection completion.

    :param response: Response from connection protocol.

    :returns: `response` unaltered.
    """

    Session.LOGGER.info(
        msg=f"Closed connection with {request.remote_addr}. "
        f"Status: {response.status_code}."
    )

    return response


# =============================================================================

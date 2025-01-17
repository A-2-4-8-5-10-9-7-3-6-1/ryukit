"""
Flask related constants.

Dependency level: 1.
"""

from base64 import b64encode
from typing import Any

from flask import Flask

from .configs import CONTENT_PATH

# =============================================================================

APP = Flask(import_name="Ryujinxkit Server")

# -----------------------------------------------------------------------------


@APP.route(rule="/")
def _() -> list[dict[str, Any]]:
    """
    Content getter-route.

    :returns: List of objects containing contents' data.
    """

    return [
        {
            "usage": usage,
            "data": b64encode(s=data).decode(),
        }
        for usage, data in zip(
            ("app-files", "system-keys", "system-registered", "meta-file"),
            (
                (CONTENT_PATH / file).read_bytes()
                for file in (
                    "app.tar",
                    "keys.tar",
                    "registered.tar",
                    "app-meta.json",
                )
            ),
        )
    ]


# =============================================================================

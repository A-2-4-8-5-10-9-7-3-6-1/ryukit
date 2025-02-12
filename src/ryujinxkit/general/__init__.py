"""
General configurations and tools.
"""

from .configs import (
    APP_AUTHOR,
    APP_VERSION,
    DATABASE_SAVE_TAG_DEFAULT,
    RYUJINX_AUTHOR,
    SOURCE_APP,
    SOURCE_KEYS,
    SOURCE_META,
    SOURCE_REGISTERED,
    UI_REFRESH_RATE,
)
from .enums import FileNode
from .formatting.decorators import apply_formatters
from .formatting.formatters import format_tag
from .session import Session

# =============================================================================

__all__ = [
    "DATABASE_SAVE_TAG_DEFAULT",
    "SOURCE_APP",
    "SOURCE_CONNECTION_ERROR_MESSAGE",
    "SOURCE_KEYS",
    "SOURCE_META",
    "SOURCE_REGISTERED",
    "APP_AUTHOR",
    "APP_VERSION",
    "RYUJINX_AUTHOR",
    "UI_REFRESH_RATE",
    "FileNode",
    "Session",
    "apply_formatters",
    "format_tag",
]

# =============================================================================

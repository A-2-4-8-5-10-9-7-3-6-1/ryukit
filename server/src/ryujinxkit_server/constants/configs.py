"""
Configuration constants.

Dependency level: 0.
"""

from os import getenv
from pathlib import Path

# =============================================================================

CONTENT_PATH = Path(getenv(key="CONTENT"))

# -----------------------------------------------------------------------------

SERVER_NAME = "RyujinxKit Server"

# =============================================================================

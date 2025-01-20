"""
Logging-related constants.

Dependency level: 1.
"""

from logging import INFO, basicConfig, getLogger

from .configs import SERVER_NAME

# =============================================================================

basicConfig(level=INFO, format="%(asctime)s - %(message)s")

# -----------------------------------------------------------------------------

LOGGER = getLogger(name=SERVER_NAME)

# =============================================================================

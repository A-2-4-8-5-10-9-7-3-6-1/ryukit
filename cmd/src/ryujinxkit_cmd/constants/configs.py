"""
Configuration constants.

Dependency level: 0.
"""

# =============================================================================

SETUP_CHUNK_SIZE = pow(2, 12)

SETUP_CONNECTION_ERROR_MESSAGE = "Couldn't connect to server."
UNPACK_SLOWDOWN: dict[str, float] = {
    "app-files": 0.2,
    "system-keys": 1,
    "system-registered": 0.01,
}

# =============================================================================

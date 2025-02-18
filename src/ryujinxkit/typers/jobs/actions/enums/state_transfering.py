"""
- dependency level 0.
"""

import enum


class Enum(str, enum.Enum):
    RESTORE = "restore"
    UPDATE = "update"

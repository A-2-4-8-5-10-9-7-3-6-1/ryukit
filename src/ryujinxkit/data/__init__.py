"""
Data-management systems.
"""

from .configs import DEFAULT_ARCHIVE_NAME
from .functions.saves import (
    archive,
    collect_saves,
    create_save,
    read_archive,
    remove_save,
    retag_save,
    use_save,
)
from .functions.source import source

__all__ = [
    "DEFAULT_ARCHIVE_NAME",
    "use_save",
    "remove_save",
    "read_archive",
    "archive",
    "source",
    "create_save",
    "collect_saves",
    "retag_save",
]

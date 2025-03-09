"""File-system setup script.

*This module has no exports.*
"""

from .resolver import Node, resolver

__all__ = []

[
    resolver[node].mkdir(parents=True, exist_ok=True)
    for node in [
        Node.RYUJINXKIT_ROAMING_DATA,
        Node.RYUJINX_ROAMING_DATA,
        Node.RYUJINXKIT_SAVE_FOLDER,
    ]
]

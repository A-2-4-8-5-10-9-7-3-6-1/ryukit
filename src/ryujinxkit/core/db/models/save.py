"""'Save table'-related models.

Exports
-------
- :class:`Save`: Model for save instances.
"""

import typing


class Save(typing.TypedDict):
    id: int
    tag: str
    created: str
    updated: str
    used: str | None
    size: int

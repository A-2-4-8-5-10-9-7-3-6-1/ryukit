"""'Save table'-related models.

Exports
-------
- :class:`Save`: Model for save instances.
"""

import datetime
import typing


class Save(typing.TypedDict):
    id: int
    tag: str
    created: datetime.datetime
    updated: datetime.datetime
    used: datetime.datetime | None
    size: int

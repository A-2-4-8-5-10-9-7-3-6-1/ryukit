"""Save-table-related models."""

import datetime
import typing


class Save(typing.NamedTuple):
    id: int
    tag: str
    created: datetime.datetime
    updated: datetime.datetime
    used: datetime.datetime | None
    size: int

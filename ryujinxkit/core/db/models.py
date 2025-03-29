"""Database models."""

import datetime
import typing

__all__ = ["RyujinxSaveModel", "RyujinxConfigModel"]


class RyujinxSaveModel(typing.NamedTuple):
    id: int
    label: str
    created: datetime.datetime
    updated: datetime.datetime
    last_used: datetime.datetime | None
    size: int


class RyujinxConfigModel(typing.NamedTuple):
    id: int
    label: str
    content: dict[str, object]
    last_used: datetime.datetime | None
    created: datetime.datetime
    updated: datetime.datetime

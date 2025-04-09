"""Database models."""

import datetime
import typing

__all__ = ["RyujinxSave", "RyujinxConfig"]


class RyujinxSave(typing.NamedTuple):
    id: int
    label: str
    created: datetime.datetime
    updated: datetime.datetime
    last_used: datetime.datetime | None
    size: int


class RyujinxConfig(typing.NamedTuple):
    id: int
    label: str
    content: dict[str, object]
    last_used: datetime.datetime | None
    created: datetime.datetime
    updated: datetime.datetime

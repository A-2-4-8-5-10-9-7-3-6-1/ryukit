import datetime
import typing

__all__ = ["Save"]


class Save(typing.TypedDict):
    id: int
    tag: str
    created: datetime.datetime
    updated: datetime.datetime
    used: datetime.datetime | None
    size: int

"""Database models."""

import typing

__all__ = ["RyujinxSave"]


class RyujinxSave(typing.TypedDict):
    id: int
    label: str
    created: str
    updated: str
    last_used: str | None
    size: int

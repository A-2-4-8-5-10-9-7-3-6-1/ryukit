"""Database models."""

from typing import TypedDict

__all__ = ["RyujinxSave"]


class RyujinxSave(TypedDict):
    id: int
    label: str
    created: str
    updated: str
    last_used: str | None
    size: int

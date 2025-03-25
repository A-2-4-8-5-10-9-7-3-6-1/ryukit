"""Save-table-related models."""

import typing


class Save(typing.TypedDict):
    id: int
    tag: str
    created: str
    updated: str
    used: str | None
    size: int

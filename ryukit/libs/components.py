"""UI-component definitions."""

import functools

import rich
import rich.box
import rich.live
import rich.status
import rich.table

__all__ = ["Status", "Live", "Table"]
Status = functools.partial(rich.status.Status, refresh_per_second=10)
Live = functools.partial(rich.live.Live, refresh_per_second=10)
Table = functools.partial(rich.table.Table, box=rich.box.SIMPLE)

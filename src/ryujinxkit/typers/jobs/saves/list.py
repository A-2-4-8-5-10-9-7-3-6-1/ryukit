"""
- dependency level 4.
"""

import collections.abc
import sqlite3

from ..actions.saves.list import action
from ..merger.merger import merger
from ..presenters.list import present


@merger(action=action, presenter=present)
def job(
    in_: collections.abc.Generator[sqlite3.Cursor],
    pole: collections.abc.Generator[None, sqlite3.Cursor],
) -> None:
    pole.send(next(in_))

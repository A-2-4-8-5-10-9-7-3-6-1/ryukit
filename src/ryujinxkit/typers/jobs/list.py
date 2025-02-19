import collections.abc
import sqlite3

from .actions.list import action
from .merger.merger import merger
from .presenters.list import present
from .presenters.typing.presenter import Presenter


@merger(action=action, presenter=present)
def job(
    in_: collections.abc.Generator[sqlite3.Cursor],
    pole: Presenter[sqlite3.Cursor],
) -> None:
    pole.send(next(in_))

import collections.abc
import sqlite3

from ...annotations import Presenter
from ...decorators.merger import merger
from .action import action
from .presenter import presenter


@merger(action=action, presenter=presenter)
def list_command(
    in_: collections.abc.Generator[sqlite3.Cursor],
    pole: Presenter[sqlite3.Cursor],
) -> None:
    pole.send(next(in_))

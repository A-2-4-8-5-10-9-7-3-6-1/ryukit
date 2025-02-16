"""
- dependency level 4.
"""

import collections.abc

from ..actions.saves.delete import action
from ..merger.merger import merger
from ..presenters.delete import present


@merger(action=action, presenter=present)
def job(in_: bool, pole: collections.abc.Generator[None, bool]) -> None:
    pole.send(in_)

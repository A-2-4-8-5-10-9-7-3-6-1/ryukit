"""
- dependency level 4.
"""

import collections.abc

from ..actions.saves.create import action
from ..merger.merger import merger
from ..presenters.create import present


@merger(action=action, presenter=present)
def job(in_: int, pole: collections.abc.Generator[None, int]) -> None:
    pole.send(in_)

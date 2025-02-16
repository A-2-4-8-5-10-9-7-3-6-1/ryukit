"""
- dependency level 4.
"""

import collections.abc

from ..actions.saves.retag import action
from ..merger.merger import merger
from ..presenters.retag import present


@merger(action=action, presenter=present)
def job(in_: bool, pole: collections.abc.Generator[None, bool]) -> None:
    pole.send(in_)

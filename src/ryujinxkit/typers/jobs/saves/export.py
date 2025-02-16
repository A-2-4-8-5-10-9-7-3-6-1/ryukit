"""
- dependency level 4.
"""

import collections.abc

from ..actions.saves.export import action
from ..merger.merger import merger
from ..presenters.export import present


@merger(action=action, presenter=present)
def job(in_: None, pole: collections.abc.Generator[None]) -> None:
    next(pole)

"""
- dependency level 2.
"""

import collections.abc

from ..actions.app.version import action
from ..merger.merger import merger
from ..presenters.version import present


@merger(action=action, presenter=present)
def job(in_: str, pole: collections.abc.Generator[None, str]) -> None:
    pole.send(in_)

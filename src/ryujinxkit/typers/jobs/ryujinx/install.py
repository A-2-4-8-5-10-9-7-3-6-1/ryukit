"""
- dependency level 3.
"""

import collections.abc

from ..actions.ryujinx.install import action
from ..merger.merger import merger
from ..presenters.install import present


@merger(action=action, presenter=present)
def job(
    in_: collections.abc.Generator[tuple[str, float]],
    pole: collections.abc.Generator[None, tuple[str, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[1] == -1:
            break

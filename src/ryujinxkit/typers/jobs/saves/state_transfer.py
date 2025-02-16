"""
- dependency level 4.
"""

import collections.abc

from ..actions.saves.state_transfer import action
from ..merger.merger import merger
from ..presenters.state_transfer import present


@merger(action=action, presenter=present)
def job(
    in_: collections.abc.Generator[tuple[str, float]],
    pole: collections.abc.Generator[None, tuple[str, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == "FAILED":
            return

    pole.send(("FINISHED", -1))

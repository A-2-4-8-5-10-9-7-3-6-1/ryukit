import collections.abc

from .actions.extract import action
from .merger.merger import merger
from .messages.extract import ExtractSignal
from .messages.primers import Primer
from .presenters.extract import present
from .presenters.types.presenter import Presenter


@merger(action=action, presenter=present)
def job(
    in_: collections.abc.Generator[tuple[ExtractSignal, float]],
    pole: Presenter[tuple[ExtractSignal, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == ExtractSignal.FAILED:
            return

    pole.send(Primer.FINISHED)

import collections.abc

from .actions.state_transfer import action
from .merger.merger import merger
from .messages.primers import Primer
from .messages.state_transfer import StateTransferSignal
from .presenters.state_transfer import present
from .presenters.types.presenter import Presenter


@merger(action=action, presenter=present)
def job(
    in_: collections.abc.Generator[tuple[StateTransferSignal, float]],
    pole: Presenter[tuple[StateTransferSignal, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == StateTransferSignal.FAILED:
            return

    pole.send(Primer.FINISHED)

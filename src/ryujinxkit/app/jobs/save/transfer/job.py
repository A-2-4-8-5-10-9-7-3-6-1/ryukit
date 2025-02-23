import collections.abc

from ...annotations import Presenter
from ...decorators.merger import merger
from ...signals import Primer
from .action import action
from .presenter import presenter
from .signals import StateTransferSignal


@merger(action=action, presenter=presenter)
def transfer_job(
    in_: collections.abc.Generator[tuple[StateTransferSignal, float]],
    pole: Presenter[tuple[StateTransferSignal, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == StateTransferSignal.FAILED:
            return

    pole.send(Primer.FINISHED)

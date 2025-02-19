import collections.abc

from .actions.install import action
from .merger.merger import merger
from .messages.install import InstallSignal
from .messages.primers import Primer
from .presenters.install import present
from .presenters.types.presenter import Presenter


@merger(action=action, presenter=present)
def job(
    in_: collections.abc.Generator[tuple[InstallSignal, float]],
    pole: Presenter[tuple[InstallSignal, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == InstallSignal.FAILED:
            return

    pole.send(Primer.FINISHED)

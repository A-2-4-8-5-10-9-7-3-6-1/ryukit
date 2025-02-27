import collections.abc

from ...annotations import Presenter
from ...decorators.merger import merger
from ...signals import Primer
from .action import action
from .presenter import present
from .signals import InstallSignal


@merger(action=action, presenter=present)
def install_command(
    in_: collections.abc.Generator[tuple[InstallSignal, float]],
    pole: Presenter[tuple[InstallSignal, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == InstallSignal.FAILED:
            return

    pole.send(Primer.FINISHED)

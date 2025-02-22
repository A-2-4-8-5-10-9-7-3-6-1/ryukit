import collections.abc

from .....libs.jobs.annotations import Presenter
from .....libs.jobs.decorators.merger import merger
from .....libs.jobs.signals import Primer
from .action import action
from .presenter import present
from .signals import InstallSignal


@merger(action=action, presenter=present)
def install_job(
    in_: collections.abc.Generator[tuple[InstallSignal, float]],
    pole: Presenter[tuple[InstallSignal, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == InstallSignal.FAILED:
            return

    pole.send(Primer.FINISHED)

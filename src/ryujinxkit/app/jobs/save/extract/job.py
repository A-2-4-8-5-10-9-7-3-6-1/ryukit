import collections.abc

from .....libs.jobs.annotations import Presenter
from .....libs.jobs.decorators.merger import merger
from .....libs.jobs.signals import Primer
from .action import action
from .presenter import presenter
from .signals import ExtractSignal


@merger(action=action, presenter=presenter)
def extract_job(
    in_: collections.abc.Generator[tuple[ExtractSignal, float]],
    pole: Presenter[tuple[ExtractSignal, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == ExtractSignal.FAILED:
            return

    pole.send(Primer.FINISHED)

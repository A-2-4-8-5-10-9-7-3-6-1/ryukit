from .....libs.jobs.annotations import Presenter
from .....libs.jobs.decorators.merger import merger
from .action import action
from .presenter import presenter


@merger(action=action, presenter=presenter)
def retag_job(in_: bool, pole: Presenter[bool]) -> None:
    pole.send(in_)

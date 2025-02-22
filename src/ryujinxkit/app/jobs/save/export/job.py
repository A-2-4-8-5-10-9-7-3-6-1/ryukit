from .....libs.jobs.annotations import Presenter
from .....libs.jobs.decorators.merger import merger
from .action import action
from .presenter import presenter


@merger(action=action, presenter=presenter)
def export_job(in_: None, pole: Presenter[None]) -> None:
    next(pole)

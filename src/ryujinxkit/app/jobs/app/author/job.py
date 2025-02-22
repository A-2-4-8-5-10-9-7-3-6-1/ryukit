from .....libs.jobs.annotations import Presenter
from .....libs.jobs.decorators.merger import merger
from .action import action
from .presenter import present


@merger(action=action, presenter=present)
def author_job(in_: str, pole: Presenter[str]) -> None:
    pole.send(in_)

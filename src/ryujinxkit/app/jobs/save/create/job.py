from ...annotations import Presenter
from ...decorators.merger import merger
from .action import action
from .presenter import presenter


@merger(action=action, presenter=presenter)
def create_job(in_: int, pole: Presenter[int]) -> None:
    pole.send(in_)

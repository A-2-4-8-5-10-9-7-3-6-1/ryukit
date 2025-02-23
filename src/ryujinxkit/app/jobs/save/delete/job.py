from ...annotations import Presenter
from ...decorators.merger import merger
from .action import action
from .presenter import presenter


@merger(action=action, presenter=presenter)
def delete_job(in_: bool, pole: Presenter[bool]) -> None:
    pole.send(in_)

from .actions.retag import action
from .merger.merger import merger
from .presenters.retag import present
from .presenters.types.presenter import Presenter


@merger(action=action, presenter=present)
def job(in_: bool, pole: Presenter[bool]) -> None:
    pole.send(in_)

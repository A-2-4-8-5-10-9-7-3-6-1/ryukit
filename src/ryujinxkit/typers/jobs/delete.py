from .actions.delete import action
from .merger.merger import merger
from .presenters.delete import present
from .presenters.typing.presenter import Presenter


@merger(action=action, presenter=present)
def job(in_: bool, pole: Presenter[bool]) -> None:
    pole.send(in_)

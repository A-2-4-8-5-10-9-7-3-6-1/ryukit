from .actions.create import action
from .merger.merger import merger
from .presenters.create import present
from .presenters.typing.presenter import Presenter


@merger(action=action, presenter=present)
def job(in_: int, pole: Presenter[int]) -> None:
    pole.send(in_)

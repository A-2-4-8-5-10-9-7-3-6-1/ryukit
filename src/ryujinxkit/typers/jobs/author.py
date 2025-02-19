from .actions.author import action
from .merger.merger import merger
from .presenters.author import present
from .presenters.typing.presenter import Presenter


@merger(action=action, presenter=present)
def job(in_: str, pole: Presenter[str]) -> None:
    pole.send(in_)

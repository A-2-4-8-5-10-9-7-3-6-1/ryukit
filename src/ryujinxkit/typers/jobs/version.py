from .actions.version import action
from .merger.merger import merger
from .presenters.types.presenter import Presenter
from .presenters.version import present


@merger(action=action, presenter=present)
def job(in_: str, pole: Presenter[str]) -> None:
    pole.send(in_)

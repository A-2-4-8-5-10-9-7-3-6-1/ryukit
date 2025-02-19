from .actions.export import action
from .merger.merger import merger
from .presenters.export import present
from .presenters.types.presenter import Presenter


@merger(action=action, presenter=present)
def job(in_: None, pole: Presenter[None]) -> None:
    next(pole)

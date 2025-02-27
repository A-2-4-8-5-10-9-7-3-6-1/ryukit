from ...annotations import Presenter
from ...decorators.merger import merger
from .action import action
from .presenter import presenter


@merger(action=action, presenter=presenter)
def export_command(in_: None, pole: Presenter[None]) -> None:
    next(pole)

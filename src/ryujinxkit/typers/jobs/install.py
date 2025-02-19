import collections.abc

from .actions.install import action
from .merger.merger import merger
from .presenters.enums.commands import Enum as Command
from .presenters.install import present
from .presenters.typing.presenter import Presenter


@merger(action=action, presenter=present)
def job(
    in_: collections.abc.Generator[tuple[str, float]],
    pole: Presenter[tuple[str, float]],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == "FAILED":
            return

    pole.send(Command.FINISHED)

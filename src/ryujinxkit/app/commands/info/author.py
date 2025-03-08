import collections.abc
import importlib.metadata

from ....core.ui.objects import console
from ...context import settings
from ..merger import merger
from ..signals import Primer

__all__ = ["author_command"]


def presenter() -> collections.abc.Generator[None, str | Primer]:
    signal = yield

    if isinstance(signal, Primer):
        return

    if settings["json"]:
        return console.print_json(data={"author": signal})

    console.print(f"{signal} @ https://github.com/{signal}")


def action() -> str:
    """
    Get app's author.

    :returns: App's author.
    """

    return importlib.metadata.metadata("ryujinxkit")["author"]


@merger(action=action, presenter=presenter)
def author_command(
    in_: str, pole: collections.abc.Generator[None, str | Primer]
) -> None:
    pole.send(in_)

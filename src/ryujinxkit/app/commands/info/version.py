import collections.abc
import importlib.metadata

from ....core.ui.console import console
from ...context import settings
from ..merger import merger
from ..signals import Primer

__all__ = ["version_command"]


def presenter() -> collections.abc.Generator[None, str | Primer]:
    signal = yield

    if isinstance(signal, Primer):
        return

    if settings["json"]:
        return console.print_json(data={"version": signal})

    console.print(f"(RyujinxKit) version {signal}")


def action() -> str:
    """
    Get app's version.

    :returns: App's version.
    """

    return importlib.metadata.version("ryujinxkit")


@merger(action=action, presenter=presenter)
def version_command(
    in_: str, pole: collections.abc.Generator[None, str | Primer]
) -> None:
    pole.send(in_)

"""Info command.

Exports
-------
- :func:`info_command`: The info command.
- :class:`InfoCommandSubject`: Options for the info command.
"""

import collections
import collections.abc
import enum
import importlib
import importlib.metadata
import typing

import rich
import rich.markdown

from ....core.ui.objects import console
from ...context import settings
from ..AP_decomp import PrimitiveSignal, merger


class InfoCommandSubject(int, enum.Enum):
    VERSION = 0
    AUTHOR = 1


def presenter() -> (
    collections.abc.Generator[
        None,
        tuple[InfoCommandSubject, dict[str, typing.Any]] | PrimitiveSignal,
    ]
):
    def id_[T](x: T) -> T:
        return x

    signal = yield

    if isinstance(signal, PrimitiveSignal):
        return

    subject, data = signal

    if settings["json"]:
        return console.print_json(data=data)

    class Configs(typing.TypedDict):
        content: str
        markup: collections.abc.Callable[[str], typing.Any] | None

    configs: dict[InfoCommandSubject, Configs] = {
        InfoCommandSubject.VERSION: {
            "content": "(RyujinxKit) version {version}",
            "markup": None,
        },
        InfoCommandSubject.AUTHOR: {
            "content": "[{author}]({link})",
            "markup": rich.markdown.Markdown,
        },
    }

    console.print(
        (configs[subject]["markup"] or id_)(
            configs[subject]["content"].format(**data)
        )
    )


def action(
    subject: InfoCommandSubject,
) -> tuple[InfoCommandSubject, dict[str, typing.Any]]:
    """
    Get app info.

    :param subject: The information's subject.

    :returns: Requested information.
    """

    match subject:
        case InfoCommandSubject.VERSION:
            return InfoCommandSubject.VERSION, {
                "version": importlib.metadata.version("ryujinxkit")
            }

        case InfoCommandSubject.AUTHOR:
            author = importlib.metadata.metadata("ryujinxkit")["author"]

            return InfoCommandSubject.AUTHOR, {
                "author": author,
                "link": f"https://github.com/{author}",
            }


@merger(action=action, presenter=presenter)
def info_command(
    in_: tuple[InfoCommandSubject, dict[str, typing.Any]],
    pole: collections.abc.Generator[
        None,
        tuple[InfoCommandSubject, dict[str, typing.Any]] | PrimitiveSignal,
    ],
) -> None:
    pole.send(in_)

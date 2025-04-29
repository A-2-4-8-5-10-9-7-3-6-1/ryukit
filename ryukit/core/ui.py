"""UI-centered definitions."""

import collections
import collections.abc
import functools
import typing

import rich
import rich.box
import rich.live
import rich.status
import rich.table
import rich.theme
import typer

__all__ = ["Status", "console", "Live", "Table", "tuned"]
console = rich.console.Console(
    theme=rich.theme.Theme({"error": "italic red"}), highlight=False
)
Status = functools.partial(rich.status.Status, refresh_per_second=10)
Live = functools.partial(rich.live.Live, refresh_per_second=10)
Table = functools.partial(rich.table.Table, box=rich.box.SIMPLE)


def tuned[R](func: collections.abc.Callable[..., R]):
    """
    Sets function defaults, as according to some greater styling.

    :param func: Funtion to be tweaked.
    :returns: 'func' with set defaults.
    """

    return typing.cast(
        collections.abc.Callable[..., R],
        {
            typer.Typer: functools.partial(typer.Typer, rich_markup_mode=None)
        }.get(typing.cast(typing.Any, func), func),
    )

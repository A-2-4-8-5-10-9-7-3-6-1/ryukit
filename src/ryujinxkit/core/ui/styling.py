"""Component-styling utilities.

Exports
-------
- :func:`styled`: Applies default styling to graphical components.
"""

# Turn into stand-alone package

import collections
import collections.abc
import inspect
import typing

import rich
import rich.box
import rich.progress
import rich.status
import rich.table
import typer

from .objects import console


def styled[**P, R](
    component: collections.abc.Callable[P, R],
) -> collections.abc.Callable[P, R]:
    """Endow a graphical component with defaults.

    :param component: The component to endow.

    :returns: The endowed component.
    """

    general_configs = {"refresh_rate": 10}
    defaults: dict[str, typing.Any] = {}
    preprocessor: collections.abc.Callable[
        P, tuple[typing.Any, typing.Any]
    ] = lambda *args, **kwargs: (args, kwargs)

    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        signature = inspect.signature(component)
        bound_args = signature.bind(*args, **kwargs)
        args, kwargs = preprocessor(*bound_args.args, **bound_args.kwargs)

        return component(*args, **(defaults | kwargs))

    match component:
        case rich.progress.Progress:
            defaults = {
                "refresh_per_second": general_configs["refresh_rate"],
                "console": console,
            }
            preprocessor = lambda *args, **kwargs: (
                tuple(
                    (
                        param
                        if not isinstance(param, str)
                        else f"[italic][colour.secondary]{param}"
                    )
                    for param in args
                ),
                kwargs,
            )

        case rich.status.Status:
            defaults = {
                "console": console,
                "refresh_per_second": general_configs["refresh_rate"],
                "spinner": "aesthetic",
                "spinner_style": "colour.primary",
            }
            preprocessor = lambda *args, **kwargs: (
                (
                    args
                    if not isinstance(args[0], str)
                    else (f"[italic][colour.secondary]{args[0]}", *args[1:])
                ),
                kwargs,
            )

        case rich.progress.SpinnerColumn:
            defaults = {"style": "colour.primary", "spinner_name": "aesthetic"}

        case rich.table.Table:
            defaults = {
                "box": rich.box.Box(
                    box="\n".join(
                        [
                            "    ",
                            "    ",
                            " -  ",
                            "    ",
                            "    ",
                            "    ",
                            "    ",
                            "    ",
                        ]
                    ),
                    ascii=True,
                )
            }

        case typer.Typer:
            defaults = {"rich_markup_mode": "rich"}

        case _:
            pass

    return inner

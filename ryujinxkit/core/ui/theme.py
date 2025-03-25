"""
Theme Guide
===========

rich.progress.Progress
----------------------

Default kwargs:

- refresh_per_second
- console

The preprocessor will add styling to every positional string renderable, \
so it's recommended to use strings for text renderables.

rich.progress.SpinnerColumn
---------------------------

Default kwargs:

- style
- spinner_name

rich.status.Status
------------------

Default kwargs:

- console
- refresh_per_second
- spinner
- spinner_style

The preprocessor will add styling to the "status" argument and expects it \
to be provided positionally.

rich.table.Table
----------------

Default kwargs:

- box

typer.Typer
-----------

Default kwargs:

- rich_markup_mode
"""

import rich
import rich.box
import rich.progress
import rich.status
import rich.table
import theming
import theming.functional_theming
import typer

from .objects import console


def _progress_PPR(*args: object, **kwargs: object):
    return (
        tuple(
            (
                arg
                if not isinstance(arg, str)
                else f"[italic][colour.secondary]{arg}"
            )
            for arg in args
        ),
        kwargs,
    )


def _status_PPR(status: object, *rest: object, **kwargs: object):
    return (
        (
            rest
            if not isinstance(status, str)
            else (f"[italic][colour.secondary]{status}", *rest)
        ),
        kwargs,
    )


general = {"refresh_rate": 10}
ui_applier = theming.functional_theming.theme_applier(
    {
        rich.progress.Progress: {
            "default_kwargs": {
                "refresh_per_second": general["refresh_rate"],
                "console": console,
            },
            "preprocessor": _progress_PPR,
        },
        rich.status.Status: {
            "default_kwargs": {
                "console": console,
                "refresh_per_second": general["refresh_rate"],
                "spinner": "aesthetic",
                "spinner_style": "colour.primary",
            },
            "preprocessor": _status_PPR,
        },
        rich.progress.SpinnerColumn: {
            "default_kwargs": {
                "style": "colour.primary",
                "spinner_name": "aesthetic",
            }
        },
        rich.table.Table: {
            "default_kwargs": {
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
        },
        typer.Typer: {"default_kwargs": {"rich_markup_mode": "rich"}},
    }
)

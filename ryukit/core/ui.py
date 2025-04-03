"""UI definitions."""

import collections.abc

import rich
import rich.box
import rich.progress
import rich.status
import rich.table
import rich.theme
import typer

from ..libs import theming

__all__ = ["console", "theme_applier"]

# ==== Objects ====

theme_extras = {
    "colour.primary": "blue",
    "colour.secondary": "none",
    "colour.accent": "#e68eef",
    "default": "italic",
}
console = rich.console.Console(
    theme=rich.theme.Theme(
        {
            "error": "red",
            "markdown.link_url": theme_extras["colour.accent"],
            **theme_extras,
        }
    ),
    style="default",
    highlight=False,
)

# ==== Theming ====


def annotate_applier[**P, R](applier: collections.abc.Callable[P, R]):
    def annotated_applier(*args: P.args, **kwargs: P.kwargs) -> R:
        """
        Hook for setting parameter defaults for UI functions.

        Theme Guide
        ===========

        rich.progress.Progress
        ----------------------

        Default kwargs:

        - refresh_per_second
        - console

        The preprocessor will add styling to every positional string renderable, so it's recommended to use strings for text renderables.

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

        The preprocessor will add styling to the "status" argument and expects it to be provided through a keyword.

        rich.table.Table
        ----------------

        Default kwargs:

        - box

        typer.Typer
        -----------

        Default kwargs:

        - rich_markup_mode
        """

        return applier(*args, **kwargs)

    return annotated_applier


def progress_PPR(*args: object, **kwargs: object):
    return (
        tuple(
            f"[italic][colour.secondary]{arg}" if isinstance(arg, str) else arg
            for arg in args
        ),
        kwargs,
    )


def status_PPR(*args: object, **kwargs: object):
    if "status" in kwargs:
        kwargs["status"] = f"[italic][colour.secondary]{kwargs["status"]}"

    return (args, kwargs)


general_theme_settings = {"refresh_rate": 10}
theme_applier = annotate_applier(
    theming.theme_applier(
        {
            rich.progress.Progress: {
                "default_kwargs": {
                    "refresh_per_second": general_theme_settings[
                        "refresh_rate"
                    ],
                    "console": console,
                },
                "preprocessor": progress_PPR,
            },
            rich.status.Status: {
                "default_kwargs": {
                    "console": console,
                    "refresh_per_second": general_theme_settings[
                        "refresh_rate"
                    ],
                    "spinner": "aesthetic",
                    "spinner_style": "colour.primary",
                },
                "preprocessor": status_PPR,
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
            typer.Typer: {"default_kwargs": {"rich_markup_mode": "markdown"}},
        }
    )
)

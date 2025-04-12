"""UI definitions."""

import collections.abc

import rich
import rich.box
import rich.live
import rich.table
import rich.theme
import typer

from ..libs import theming

__all__ = ["console", "theme_applier"]

# MARK: Objects

theme_extras = {
    "colour.primary": "blue",
    "colour.secondary": "none",
    "colour.accent": "#e68eef",
    "default": "none",
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

# MARK: Theming


def annotate_applier[**P, R](applier: collections.abc.Callable[P, R]):
    def annotated_applier(*args: P.args, **kwargs: P.kwargs) -> R:
        """
        Hook for setting parameter defaults for UI functions.

        Theme Guide
        ===========

        rich.table.Table
        ----------------
        Default kwargs: box

        rich.live.Live
        --------------
        Default kwargs: refresh_per_second

        typer.Typer
        -----------
        Default kwargs: rich_markup_mode
        """

        return applier(*args, **kwargs)

    return annotated_applier


general_theme_settings = {"refresh_rate": 10}
theme_applier = annotate_applier(
    theming.theme_applier(
        {
            rich.live.Live: {
                "default_kwargs": {
                    "refresh_per_second": general_theme_settings[
                        "refresh_rate"
                    ],
                    "console": console,
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
)

"""Presentation-layer definitions."""

import collections.abc

import rich
import rich.box
import rich.live
import rich.status
import rich.table
import rich.theme
import typer

from ..libs import theming

__all__ = ["theme"]

# MARK: Theming


def annotate_applier[**P, R](applier: collections.abc.Callable[P, R]):
    def annotated_applier(*args: P.args, **kwargs: P.kwargs) -> R:
        """
        Sets defaults on UI-based functions.

        Theme Guide
        -----------

        - rich.table.Table(defaults=[box])
        - rich.live.Live(defaults=[refresh_per_second])
        - rich.Typer(defaults=[rich_markup_mode])
        - rich.console.Console(defaults=[theme, highlight])
        - rich.status.Status(defaults=[refresh_per_second])
        """

        return applier(*args, **kwargs)

    return annotated_applier


common_settings = {"refresh_rate": 10}
theme = annotate_applier(
    theming.theme_applier(
        {
            rich.status.Status: {
                "default_kwargs": {
                    "refresh_per_second": common_settings["refresh_rate"]
                }
            },
            rich.console.Console: {
                "default_kwargs": {
                    "theme": rich.theme.Theme({"error": "italic red"}),
                    "highlight": False,
                }
            },
            rich.live.Live: {
                "default_kwargs": {
                    "refresh_per_second": common_settings["refresh_rate"]
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

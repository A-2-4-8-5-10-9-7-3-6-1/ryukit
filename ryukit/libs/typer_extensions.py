"""For typer implementations."""

import functools
from collections.abc import Callable

import click
import typer

from ..utils import patterns

__all__ = ["then_terminate"]
STATE = {"started": False}


@patterns.use
def _():
    initial = typer.Typer.__call__

    @functools.wraps(initial)
    def inner(*args: ..., **kwargs: ...):
        STATE["started"] = True
        return initial(*args, **kwargs)

    typer.Typer.__call__ = inner


def then_terminate[**P](func: Callable[P, None], /):
    """Force termination, via an exception, after execution of subsequent function."""

    @functools.wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs):
        func(*args, **kwargs)
        if STATE["started"]:
            raise click.exceptions.Exit()

    return inner

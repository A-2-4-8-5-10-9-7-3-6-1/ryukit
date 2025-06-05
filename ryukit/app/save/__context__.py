import pathlib
import shutil
from collections.abc import Sequence

import typer

from ...utils import patterns
from ..__context__ import *

__all__ = ["HELPERS", "SYSTEM_CONFIGS", "command", "PARSERS"]
save = typer.Typer(name="save")
command = save.command
app.add_typer(save)


@save.callback()
def _():
    """Manage save buckets."""


@patterns.dict_decorator(HELPERS, key="channel_save_bucket")
def _(id_: int, /, *, upstream: bool):
    def rotate[T](values: Sequence[T]):
        return (iter if upstream else reversed)(values)

    for source, dest in map(
        rotate,
        map(
            tuple,
            map(
                lambda p: map(pathlib.Path, p),
                (
                    (x.format(id=id_), y)
                    for x, y in SYSTEM_CONFIGS["save_buckets"]["flow"].items()
                ),
            ),
        ),
    ):
        if dest.exists():
            shutil.rmtree(dest)
        if not source.exists():
            continue
        shutil.copytree(source, dest)

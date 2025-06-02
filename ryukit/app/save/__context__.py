import pathlib
import shutil
from collections.abc import Sequence

import typer

from ..__context__ import *

__all__ = [
    "channel_save_bucket",
    "USER_CONFIGS",
    "INTERNAL_CONFIGS",
    "command",
    "console",
    "bucket",
]
save = typer.Typer(name="save", no_args_is_help=True)
command = save.command
app.add_typer(save)


@save.callback()
def _():
    """Manage save buckets."""


def channel_save_bucket(bucket_id: int, /, *, upstream: bool):
    """
    Channel content between a save bucket and Ryujinx.

    :param upstream: Set as true to channel from the bucket to Ryujinx, and as false to do the reverse.
    :param bucket_id: ID belonging to the subject save bucket.
    """

    def rotate[T](values: Sequence[T]):
        return (iter if upstream else reversed)(values)

    for source, dest in map(
        rotate,
        map(
            tuple,
            map(
                lambda p: map(pathlib.Path, p),
                (
                    (x.format(id=bucket_id), y)
                    for x, y in INTERNAL_CONFIGS["save_buckets"][
                        "flow"
                    ].items()
                ),
            ),
        ),
    ):
        if dest.exists():
            shutil.rmtree(dest)
        if not source.exists():
            continue
        shutil.copytree(source, dest)

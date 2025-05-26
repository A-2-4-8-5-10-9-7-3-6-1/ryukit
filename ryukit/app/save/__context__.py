import contextlib
import pathlib
import shutil
from collections.abc import Sequence

import typer

from ...libs import db
from ..__context__ import *

__all__ = ["channel_save_bucket", "bucket", "command"]
save = typer.Typer(name="save")
command = save.command
app.add_typer(save)


@save.callback()
def _():
    "Manage your save buckets."


def channel_save_bucket(bucket_id: int, /, *, upstream: bool):
    """
    Channel content between a save bucket and Ryujinx.

    :param upstream: Set as true to channel from the bucket to Ryujinx, and as false to do the reverse.
    :param bucket_id: ID belonging to the subject save bucket.
    :raises RuntimeError: If Ryujinx is not installed.
    """

    def rotate[T](values: Sequence[T]):
        return (iter if upstream else reversed)(values)

    if not INTERSESSION_STATE["ryujinx_meta"]:
        console.print(
            "[error]Couldn't detect a Ryujinx installation.",
            "└── Did you run `install_ryujinx`?",
            sep="\n",
        )
        raise typer.Exit(1)
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


@contextlib.contextmanager
def bucket(id_: int, /):
    """
    Get a save bucket from an ID.

    :param id_: The bucket's ID.
    :raises typer.Exit: If the bucket doesn't exist.
    """

    with db.client() as client:
        save = client.get(db.RyujinxSave, {"id": id_})
        if not save:
            console.print(f"[error]No bucket with ID '{id_}'.")
            raise typer.Exit(1)
        yield client, save

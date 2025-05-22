import pathlib
import shutil
from collections.abc import Sequence
from typing import Literal

import typer
from typer import Typer

from ...libs import db
from ..__context__ import *

__all__ = ["channel_save_bucket", "parser", "command"]
save = Typer(name="save")
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
                    (x.format(instance_id=bucket_id), y)
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


def parser(type_: Literal["bucket_id"], /):
    """
    Get input parser for type 'type_'.

    :param type_: The type of parser required.
    :returns: A parser for the given type.
    """

    match type_:
        case "bucket_id":

            def parser(id_: str):
                with db.connect() as conn:
                    if not conn.execute(
                        """
                        SELECT
                            COUNT(*)
                        FROM
                            ryujinx_saves
                        WHERE
                            id = :id
                        """,
                        {"id": id_},
                    ).fetchone()[0]:
                        console.print(f"[error]No bucket with ID '{id_}'.")
                        raise typer.Exit(1)
                return id_

            return parser

import shutil
import typing

import typer

from ...core import db
from ...core.fs import File
from ...core.ui import console
from .__context__ import *

__all__ = []


@save.command(name="drop")
def _(
    buckets: typing.Annotated[
        list[int],
        typer.Argument(
            help="The IDs of your to-be-deleted save buckets.",
            show_default=False,
        ),
    ],
):
    """
    Delete save buckets.

    WARNING: There's no going back...
    """

    question_marks = ", ".join("?" for _ in range(len(buckets)))
    with db.connect() as conn:
        deleted: int
        (deleted,) = conn.execute(
            f"""
            SELECT
                COUNT(*)
            FROM
                ryujinx_saves
            WHERE
                id IN ({question_marks});
            """,
            buckets,
        ).fetchone()
        conn.execute(
            f"""
            DELETE FROM 
                ryujinx_saves
            WHERE
                id IN ({question_marks});
            """,
            buckets,
        )
    any(
        shutil.rmtree(File.SAVE_INSTANCE_FOLDER(instance_id=id_))
        for id_ in buckets
        if not File.SAVE_INSTANCE_FOLDER(instance_id=id_).exists()
    )
    console.print(f"Deleted {deleted} bucket(s).")

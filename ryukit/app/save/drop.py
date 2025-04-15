import shutil
import sqlite3
import typing

import typer

from ryukit.core import presentation

from ...core import db, fs
from ...utils import typer_builder

__all__ = ["typer_builder_args"]


def command(
    ids: typing.Annotated[
        list[int],
        typer.Argument(
            metavar="ID...",
            help="The IDs of your to-be-deleted save buckets.",
            show_default=False,
        ),
    ],
):
    """
    Delete save buckets.

    [yellow]:warning:[/yellow] There's no going back...
    """

    question_marks = ", ".join("?" for _ in range(len(ids)))

    with db.theme_applier(sqlite3.connect)("DATABASE") as conn:
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
            ids,
        ).fetchone()

        conn.execute(
            f"""
            DELETE FROM 
                ryujinx_saves
            WHERE
                id IN ({question_marks});
            """,
            ids,
        )

    for id_ in ids:
        if not fs.File.SAVE_INSTANCE_FOLDER(instance_id=id_).exists():
            continue

        shutil.rmtree(fs.File.SAVE_INSTANCE_FOLDER(instance_id=id_))

    presentation.console.print(f"Deleted {deleted} bucket(s).")


typer_builder_args: typer_builder.TyperBuilderArgs = {"command": command}

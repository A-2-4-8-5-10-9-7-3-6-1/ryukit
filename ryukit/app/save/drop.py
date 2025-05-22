import shutil
from typing import Annotated

import typer

from ryukit.app.save.__context__ import command, console, parser
from ryukit.libs import db, paths


@command("drop")
def _(
    buckets: Annotated[
        list[int],
        typer.Argument(
            help="The IDs of your to-be-deleted save buckets.",
            show_default=False,
            parser=parser("bucket_id"),
        ),
    ],
):
    """
    Delete save buckets.

    WARNING: There's no going back...
    """

    question_marks = ", ".join("?" for _ in range(len(buckets)))
    with db.connect() as conn:
        conn.execute(
            f"""
            DELETE FROM 
                ryujinx_saves
            WHERE
                id IN ({question_marks})
            """,
            buckets,
        )
    any(
        shutil.rmtree(
            paths.SAVE_INSTANCE_DIR.format(instance_id=id_), ignore_errors=True
        )
        for id_ in buckets
    )
    console.print("Buckets deleted.")

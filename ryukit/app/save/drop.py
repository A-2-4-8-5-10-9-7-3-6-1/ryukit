import pathlib
import shutil
import typing

import typer

from ryukit.app.__context__ import console
from ryukit.app.save.__context__ import command, parser
from ryukit.core import db
from ryukit.core.fs import File


@command("drop")
def _(
    buckets: typing.Annotated[
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
                id IN ({question_marks});
            """,
            buckets,
        )
    any(
        shutil.rmtree(File.SAVE_INSTANCE_DIR.format(instance_id=id_))
        for id_ in buckets
        if not pathlib.Path(
            File.SAVE_INSTANCE_DIR.format(instance_id=id_)
        ).exists()
    )
    console.print("Buckets deleted.")

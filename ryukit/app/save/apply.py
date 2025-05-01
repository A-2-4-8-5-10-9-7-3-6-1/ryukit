import typing

import typer

from ryukit.app.__context__ import console
from ryukit.app.save.__context__ import channel_save_bucket, command, parser
from ryukit.core import db


@command("apply")
def _(
    bucket: typing.Annotated[
        int,
        typer.Argument(
            help="ID of bucket to apply.", parser=parser("bucket_id")
        ),
    ],
):
    """
    Apply data from a save bucket into Ryujinx.

    WARNING: This will overwrite files for Ryujinx. Unless certain, save your data.
    """

    with db.connect() as conn:
        channel_save_bucket(bucket, upstream=True)
        conn.execute(
            """
            UPDATE
                ryujinx_saves
            SET
                last_used = CURRENT_TIMESTAMP
            WHERE
                id = :id;
            """,
            {"id": bucket},
        )
    console.print("Save applied.")

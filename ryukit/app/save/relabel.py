from typing import Annotated

import typer

from ryukit.app.save.__context__ import command, console, parser
from ryukit.libs import db


@command("relabel")
def _(
    bucket: Annotated[
        int,
        typer.Argument(
            help="ID of bucket to update.",
            show_default=False,
            parser=parser("bucket_id"),
        ),
    ],
    as_: Annotated[
        str,
        typer.Option(
            "--as", help="New label for the bucket.", show_default=False
        ),
    ],
):
    """Relabel an existing bucket."""

    with db.connect() as conn:
        conn.execute(
            """
            UPDATE
                ryujinx_saves
            SET
                label = :label
            WHERE
                id = :id
            """,
            {"label": as_, "id": bucket},
        )
    console.print("Label updated.")

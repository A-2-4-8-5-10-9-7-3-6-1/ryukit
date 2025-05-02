import typing

import typer

from ryukit.app.__context__ import console
from ryukit.app.save.__context__ import command, parser
from ryukit.core import db


@command("relabel")
def _(
    bucket: typing.Annotated[
        int,
        typer.Argument(
            help="ID of bucket to update.",
            show_default=False,
            parser=parser("bucket_id"),
        ),
    ],
    as_: typing.Annotated[
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
                id = :id;
            """,
            {"label": as_, "id": bucket},
        )
    console.print("Label updated.")

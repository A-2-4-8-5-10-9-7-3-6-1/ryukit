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
    set_to: typing.Annotated[
        str, typer.Option(help="New label for the bucket.", show_default=False)
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
            {"label": set_to, "id": bucket},
        )
    console.print("Label updated.")

import pathlib
import typing

import typer

from ryukit.app.__context__ import console
from ryukit.app.save.__context__ import channel_save_bucket, command, parser
from ryukit.libs import db
from ryukit.libs.fs import File
from ryukit.utils import calculator


@command("pull")
def _(
    into: typing.Annotated[
        int,
        typer.Argument(
            help="ID of bucket to pull into.",
            show_default=False,
            parser=parser("bucket_id"),
        ),
    ],
):
    """Pull data from Ryujinx into a save bucket."""

    with db.connect() as conn:
        channel_save_bucket(into, upstream=False)
        size = sum(
            path.stat().st_size if path.is_file() else 0
            for path in pathlib.Path(
                File.SAVE_INSTANCE_DIR.format(instance_id=into)
            ).glob("**")
        )
        conn.execute(
            """
            UPDATE
                ryujinx_saves
            SET
                size = :size
            WHERE
                id = :id;
            """,
            {"id": into, "size": size},
        )
    console.print(
        "Updated bucket.",
        f"└── Bucket is now of size {calculator.megabytes(size):.1f}MB.",
        sep="\n",
    )

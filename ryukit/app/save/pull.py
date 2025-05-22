import pathlib
from typing import Annotated

import typer

from ryukit.app.save.__context__ import (
    channel_save_bucket,
    command,
    console,
    parser,
)
from ryukit.libs import db, paths
from ryukit.utils import calculator


@command("pull")
def _(
    into: Annotated[
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
                paths.SAVE_INSTANCE_DIR.format(instance_id=into)
            ).glob("**")
        )
        conn.execute(
            """
            UPDATE
                ryujinx_saves
            SET
                size = :size
            WHERE
                id = :id
            """,
            {"id": into, "size": size},
        )
    console.print(
        "Updated bucket.",
        f"└── Bucket is now of size {calculator.megabytes(size):.1f}MB.",
        sep="\n",
    )

import typing

import typer

from ...core import db
from ...core.fs import File
from ...core.ui import console
from ...utils import calculator
from .__context__ import *

__all__ = []


@save.command(name="pull")
def _(
    into: typing.Annotated[
        int,
        typer.Argument(help="ID of bucket to pull into.", show_default=False),
    ],
):
    """Pull data from Ryujinx into a save bucket."""

    if not save_bucket_exists(into):
        console.print("[error]Unrecognized ID.")
        raise typer.Exit(1)
    with db.connect() as conn:
        try:
            channel_save_bucket(into, upstream=False)
        except RuntimeError:
            console.print(
                "[error]Failed to apply save.",
                "└── [italic]Is Ryujinx installed?",
                sep="\n",
            )
            raise typer.Exit(1)
        size = sum(
            path.stat().st_size if path.is_file() else 0
            for path in File.SAVE_INSTANCE_FOLDER(instance_id=into).glob("**")
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
        f"└── [italic]Bucket is now of size {calculator.megabytes(size):.1f}MB.",
        sep="\n",
    )

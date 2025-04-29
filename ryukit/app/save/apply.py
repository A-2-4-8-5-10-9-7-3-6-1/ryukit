import typing

import typer

from ...core import db
from ...core.ui import console
from .__context__ import *

__all__ = []


@save.command(name="apply")
def _(
    bucket: typing.Annotated[
        int, typer.Argument(help="ID of bucket to apply.")
    ],
):
    """
    Apply data from a save bucket into Ryujinx.

    WARNING: This will overwrite files for Ryujinx. Unless certain, save your data.
    """

    if not save_bucket_exists(bucket):
        console.print("[error]Unrecognized ID.")
        raise typer.Exit(1)
    with db.connect() as conn:
        try:
            channel_save_bucket(bucket, upstream=True)
        except RuntimeError:
            console.print(
                "[error]Failed to apply save.",
                "└── [italic]Is Ryujinx installed?",
                sep="\n",
            )
            raise typer.Exit(1)
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

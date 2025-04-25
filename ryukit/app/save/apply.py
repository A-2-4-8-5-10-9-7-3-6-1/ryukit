import typing

import typer

from ...core import db, display
from ...utils import common_logic
from . import __typer__

__all__ = []


@__typer__.save.command(name="apply")
def _(
    bucket: typing.Annotated[
        int, typer.Argument(help="ID of bucket to apply.")
    ],
):
    """
    Apply data from a save bucket into Ryujinx.

    WARNING: This will overwrite files for Ryujinx. Unless certain, save your data.
    """

    if not common_logic.save_bucket_exists(bucket):
        display.console.print("[error]Unrecognized ID.")
        raise typer.Exit(1)
    with db.connect() as conn:
        try:
            common_logic.channel_save_bucket(bucket, upstream=True)
        except RuntimeError:
            display.console.print(
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
    display.console.print("Save applied.")

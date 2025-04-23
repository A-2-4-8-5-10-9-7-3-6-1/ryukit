import typing

import typer

from ...core import db, display, fs
from ...utils import calculator, common_logic
from . import __typer__

__all__ = []


@__typer__.save.command(name="pull")
def _(
    into: typing.Annotated[
        int,
        typer.Argument(help="ID of bucket to pull into.", show_default=False),
    ],
):
    """Pull data from Ryujinx into a save bucket."""

    if not common_logic.save_bucket_exists(into):
        display.console.print("[error]Unrecognized ID.")
        raise typer.Exit(1)
    with db.connect() as conn:
        try:
            common_logic.channel_save_bucket(into, upstream=False)
        except RuntimeError:
            display.console.print(
                "[error]Failed to apply save.",
                "└── [italic]Is Ryujinx installed?",
                sep="\n",
            )
            raise typer.Exit(1)
        size = sum(
            path.stat().st_size if path.is_file() else 0
            for path in fs.File.SAVE_INSTANCE_FOLDER(instance_id=into).glob(
                "**"
            )
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
    display.console.print(
        "Updated bucket.",
        f"└── [italic]Bucket is now of size {calculator.megabytes(size):.1f}MB.",
        sep="\n",
    )

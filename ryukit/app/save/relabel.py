import typing

import typer

from ...core import db, display
from ...utils import common_logic
from . import __typer__

__all__ = []


@__typer__.save.command(name="relabel")
def _(
    bucket: typing.Annotated[
        int, typer.Argument(help="ID of bucket to update.", show_default=False)
    ],
    set_to: typing.Annotated[
        str, typer.Option(help="New label for the bucket.", show_default=False)
    ],
):
    """Relabel an existing bucket."""

    if not common_logic.save_bucket_exists(bucket):
        display.console.print("[error]Unrecognized ID.")
        raise typer.Exit(1)
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
    display.console.print("Label updated.")

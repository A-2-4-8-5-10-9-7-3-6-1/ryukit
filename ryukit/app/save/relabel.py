import sqlite3
import typing

import rich
import typer

from ryukit.core import presentation

from ...core import db
from ...utils import common_logic, typer_builder

__all__ = ["typer_builder_args"]


def command(
    id_: typing.Annotated[
        int,
        typer.Argument(
            metavar="ID", help="ID of bucket to update.", show_default=False
        ),
    ],
    label: typing.Annotated[
        str,
        typer.Argument(help="A new label for the bucket.", show_default=False),
    ],
):
    """Relabel an existing bucket."""

    console = presentation.theme(rich.console.Console)()

    if not common_logic.save_bucket_exists(id_):
        console.print("[error]Unrecognized ID.")

        raise typer.Exit(1)

    with db.theme(sqlite3.connect)("DATABASE") as conn:
        conn.execute(
            """
            UPDATE
                ryujinx_saves
            SET
                label = :label
            WHERE
                id = :id;
            """,
            {"label": label, "id": id_},
        )

    console.print("Label updated.")


typer_builder_args: typer_builder.BuilderArgs = {"command": command}

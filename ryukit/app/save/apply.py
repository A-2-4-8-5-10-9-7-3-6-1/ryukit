import sqlite3
import typing

import rich
import typer

from ...core import db, presentation
from ...utils import common_logic, typer_builder

__all__ = ["typer_builder_args"]


def command(
    id_: typing.Annotated[
        int, typer.Argument(metavar="ID", help="ID of bucket to deploy from.")
    ],
):
    """
    Apply data from a save bucket into Ryujinx.

    [yellow]:warning:[/yellow] This will overwrite files for Ryujinx. Unless certain, save your data.
    """

    console = presentation.theme(rich.console.Console)()

    if not common_logic.save_bucket_exists(id_):
        console.print("[error]Unrecognized ID.")

        raise typer.Exit(1)

    with db.theme(sqlite3.connect)("DATABASE") as conn:
        try:
            common_logic.channel_save_bucket(id_, upstream=True)

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
            {"id": id_},
        )

    console.print("Save applied.")


typer_builder_args: typer_builder.BuilderArgs = {"command": command}

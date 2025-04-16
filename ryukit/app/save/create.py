import datetime
import sqlite3
import typing

import rich
import typer

from ryukit.core import presentation

from ...core import db
from ...utils import typer_builder

__all__ = ["typer_builder_args"]


def command(
    label: typing.Annotated[
        str, typer.Argument(help="A label for your save.")
    ] = f"save{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}",
):
    """
    Create a save bucket.

    The created bucket will be empty. You'll use the save-pull command to populate it.
    """

    console = presentation.theme(rich.console.Console)()

    with db.theme(sqlite3.connect)("DATABASE") as conn:
        id_ = conn.execute(
            """
            INSERT INTO 
                ryujinx_saves (label)
            VALUES 
                (:label);
            """,
            {"label": label},
        ).lastrowid

    console.print(f"Bucket '{label}' created with ID {id_}.")


typer_builder_args: typer_builder.BuilderArgs = {"command": command}

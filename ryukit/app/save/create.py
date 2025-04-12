import datetime
import sqlite3
import typing

import typer

from ryukit.core import ui

from ...core import db
from ...helpers import typer_builder

__all__ = ["typer_builder_args"]
default_label = f"Save{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}"


def command(
    label: typing.Annotated[
        str, typer.Argument(help="A label for your save.")
    ] = default_label,
):
    """
    Create a save bucket.

    [blue]:information:[/blue] The created bucket will be empty. You'll use the save-pull command to populate it.
    """

    with db.theme_applier(sqlite3.connect)("DATABASE") as conn:
        id_ = conn.execute(
            """
            INSERT INTO 
                ryujinx_saves (label)
            VALUES 
                (:label)
            """,
            {"label": label},
        ).lastrowid

    ui.console.print(f"Created save bucket '{label}' with ID {id_}.")


typer_builder_args: typer_builder.TyperBuilderArgs = {
    "command": command,
    "typer_args": [{"rich_help_panel": "Life Cycle Commands"}],
}

import datetime
import typing

import typer

from ryukit.app.__context__ import console
from ryukit.app.save.__context__ import command
from ryukit.core import db


@command("create")
def _(
    with_label: typing.Annotated[
        str, typer.Argument(help="A label for your save.")
    ] = f"save{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}",
):
    """
    Create a save bucket.

    The created bucket will be empty. You'll use the save-pull command to populate it.
    """

    with db.connect() as conn:
        id_ = conn.execute(
            """
            INSERT INTO 
                ryujinx_saves (label)
            VALUES 
                (:label);
            """,
            {"label": with_label},
        ).lastrowid
    console.print(f"Bucket {id_} created with label '{with_label}'.")

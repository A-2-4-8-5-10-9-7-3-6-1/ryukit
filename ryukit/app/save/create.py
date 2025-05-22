import datetime
from typing import Annotated

import typer

from ryukit.app.save.__context__ import command, console
from ryukit.libs import db


@command("create")
def _(
    with_label: Annotated[
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
                (:label)
            """,
            {"label": with_label},
        ).lastrowid
    console.print(f"Bucket {id_} created with label '{with_label}'.")

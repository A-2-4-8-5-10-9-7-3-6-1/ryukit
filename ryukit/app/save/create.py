import datetime
from typing import Annotated

import typer

from ...app.save.__context__ import command, console
from ...libs import db

__all__ = ["create"]


@command("create")
def create(
    with_label: Annotated[
        str, typer.Argument(help="A label for your save.")
    ] = f"save{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}",
):
    """
    Create a save bucket.

    The created bucket will be empty. You'll use the save-pull command to populate it.
    """

    save = db.RyujinxSave(label=with_label)
    with db.client() as client:
        client.add(save)
        client.flush()
        console.print(f"Bucket {save.id} created with label '{with_label}'.")

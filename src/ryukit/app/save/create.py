import datetime
from typing import Annotated

import rich
import typer

from ...libs import db
from .__context__ import command

__all__ = []


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

    save = db.RyujinxSave(label=with_label)
    with db.client() as client:
        client.add(save)
        client.flush()
        rich.print(f"Bucket was created with ID {save.id}.")

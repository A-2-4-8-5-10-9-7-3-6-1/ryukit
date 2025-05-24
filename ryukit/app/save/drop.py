import shutil
from typing import Annotated

import typer

from ...app.save.__context__ import bucket, command, console
from ...libs import paths


@command("drop")
def drop(
    buckets: Annotated[
        list[int],
        typer.Argument(
            help="The IDs of your to-be-deleted save buckets.",
            show_default=False,
        ),
    ],
):
    """
    Delete save buckets.

    WARNING: There's no going back...
    """

    for context in map(bucket, buckets):
        with context as (conn, save):
            conn.delete(save)
            shutil.rmtree(
                paths.SAVE_INSTANCE_DIR.format(instance_id=save.id),
                ignore_errors=True,
            )
            console.print(f"Deleted bucket '{save.id}'.")

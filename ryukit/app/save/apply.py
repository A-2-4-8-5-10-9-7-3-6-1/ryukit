import datetime
from typing import Annotated

import typer

from ...app.save.__context__ import (
    bucket,
    channel_save_bucket,
    command,
    console,
)


@command("apply")
def apply(
    bucket_: Annotated[
        int, typer.Argument(metavar="BUCKET", help="ID of bucket to apply.")
    ],
):
    """
    Apply data from a save bucket into Ryujinx.

    WARNING: This will overwrite files for Ryujinx. Unless certain, save your data.
    """

    channel_save_bucket(bucket_, upstream=True)
    with bucket(bucket_) as (_, save):
        save.last_used = datetime.datetime.now(datetime.timezone.utc)
    console.print("Save applied.")

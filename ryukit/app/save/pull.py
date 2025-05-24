from typing import Annotated

import typer

from ... import utils
from ...app.save.__context__ import (
    bucket,
    channel_save_bucket,
    command,
    console,
)
from ...libs import paths


@command("pull")
def pull(
    into: Annotated[
        int,
        typer.Argument(help="ID of bucket to pull into.", show_default=False),
    ],
):
    """Pull data from Ryujinx into a save bucket."""

    channel_save_bucket(into, upstream=False)
    with bucket(into) as (_, save):
        save.size = utils.size(
            paths.SAVE_INSTANCE_DIR.format(instance_id=into), sizing="dir"
        )
        console.print(
            "Updated bucket.",
            f"└── Bucket is now of size {utils.megabytes(save.size):.1f}MB.",
            sep="\n",
        )

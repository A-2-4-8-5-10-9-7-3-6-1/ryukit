from typing import Annotated

import rich
import typer

from ...app.save.__context__ import HELPERS, command
from ...libs import paths
from ...utils import misc

__all__ = []


@command("pull")
def _(
    into: Annotated[
        int,
        typer.Argument(help="ID of bucket to pull into.", show_default=False),
    ],
):
    """Pull data from Ryujinx into a save bucket."""

    with into as (_, save):
        HELPERS["channel_save_bucket"](save.id, upstream=False)
        save.size = misc.size(
            paths.SAVE_INSTANCE_DIR.format(id=save.id), sizing="dir"
        )
        rich.print(
            "Updated bucket.",
            f"└── Bucket is now of size {misc.megabytes(save.size):.1f}MB.",
            sep="\n",
        )

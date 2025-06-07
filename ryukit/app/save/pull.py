from typing import Annotated

import rich
import rich.tree
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
        tree = rich.tree.Tree("Updated bucket.")
        tree.add(f"Bucket size is {misc.megabytes(save.size):.1f}MB.")
        rich.print(tree)

import contextlib
from typing import Annotated

import rich
import rich.tree
import sqlalchemy
import sqlalchemy.orm
import typer

from ...libs import db, paths
from ...utils import misc
from ..__context__ import PARSERS, channel_save_bucket
from .__context__ import command

__all__ = []


@command("pull")
def _(
    into: Annotated[
        contextlib.AbstractContextManager[
            tuple[sqlalchemy.orm.Session, db.RyujinxSave]
        ],
        typer.Argument(
            help="ID of bucket to pull into.",
            show_default=False,
            parser=PARSERS["bucket"],
        ),
    ],
):
    """Pull data from Ryujinx into a save bucket."""

    with into as (_, save):
        channel_save_bucket(save.id, upstream=False)
        save.size = misc.size(
            paths.SAVE_INSTANCE_DIR.format(id=save.id), sizing="dir"
        )
        tree = rich.tree.Tree("Updated bucket.")
        tree.add(f"Bucket size is {misc.megabytes(save.size):.1f}MB.")
        rich.print(tree)

import contextlib
from typing import Annotated

import sqlalchemy
import sqlalchemy.orm
import typer

from ... import utils
from ...app.save.__context__ import HELPERS, PARSERS, command, console
from ...libs import db, paths

__all__ = ["pull"]


@command("pull")
def pull(
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
        HELPERS["channel_save_bucket"](save.id, upstream=False)
        save.size = utils.size(
            paths.SAVE_INSTANCE_DIR.format(id=save.id), sizing="dir"
        )
        console.print(
            "Updated bucket.",
            f"└── Bucket is now of size {utils.megabytes(save.size):.1f}MB.",
            sep="\n",
        )

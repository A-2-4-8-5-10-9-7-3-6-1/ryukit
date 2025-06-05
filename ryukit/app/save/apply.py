import datetime
from typing import Annotated

import rich
import sqlalchemy
import sqlalchemy.orm
import typer

from ryukit.libs import db

from ...app.save.__context__ import PARSERS, command

__all__ = []


@command("apply")
def _(
    bucket: Annotated[
        contextlib.AbstractContextManager[
            tuple[sqlalchemy.orm.Session, db.RyujinxSave]
        ],
        typer.Argument(
            help="ID of bucket to apply.",
            parser=PARSERS["bucket"],
            show_default=False,
        ),
    ],
):
    """
    Apply data from a save bucket into Ryujinx.

    WARNING: This will overwrite files for Ryujinx. Unless certain, save your data.
    """

    channel_save_bucket(bucket_, upstream=True)
    with bucket(bucket_) as (_, save):
        save.last_used = datetime.datetime.now(datetime.timezone.utc)
    rich.print("Save applied.")

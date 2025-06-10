import contextlib
import datetime
from typing import Annotated

import rich
import sqlalchemy
import sqlalchemy.orm
import typer

from ...libs import db
from ..__context__ import PARSERS, channel_save_bucket
from .__context__ import command

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

    with bucket as (_, save):
        channel_save_bucket(save.id, upstream=True)
        save.last_used = datetime.datetime.now(datetime.timezone.utc)
    rich.print("Save applied.")

import contextlib
from typing import Annotated

import sqlalchemy
import sqlalchemy.orm
import typer

from ...app.save.__context__ import PARSERS, command, console
from ...libs import db

__all__ = ["relabel"]


@command("relabel")
def relabel(
    bucket: Annotated[
        contextlib.AbstractContextManager[
            tuple[sqlalchemy.orm.Session, db.RyujinxSave]
        ],
        typer.Argument(
            metavar="BUCKET",
            help="ID of bucket to update.",
            show_default=False,
            parser=PARSERS["bucket"],
        ),
    ],
    as_: Annotated[
        str,
        typer.Argument(
            metavar="AS", help="New label for the bucket.", show_default=False
        ),
    ],
):
    """Relabel an existing bucket."""

    with bucket as (_, save):
        save.label = as_
    console.print("Label updated.")

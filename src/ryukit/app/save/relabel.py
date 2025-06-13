import contextlib
from typing import Annotated

import rich
import sqlalchemy
import sqlalchemy.orm
import typer

from ...libs import db
from ..__context__ import PARSERS
from .__context__ import command

__all__ = []


@command("relabel")
def _(
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
    rich.print("Label updated.")

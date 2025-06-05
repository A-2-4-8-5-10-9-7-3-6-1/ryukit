from typing import Annotated

import rich
import sqlalchemy
import sqlalchemy.orm
import typer

from ...app.save.__context__ import command
from ...libs import db

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
        ),
    ],
    as_: Annotated[
        str,
        typer.Option(
            "--as", help="New label for the bucket.", show_default=False
        ),
    ],
):
    """Relabel an existing bucket."""

    with bucket(bucket_) as (_, save):
        save.label = as_
    rich.print("Label updated.")

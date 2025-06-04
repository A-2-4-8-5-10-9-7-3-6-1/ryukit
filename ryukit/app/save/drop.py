import contextlib
import shutil
from typing import Annotated, Any, cast

import sqlalchemy
import sqlalchemy.orm
import typer

from ...app.save.__context__ import PARSERS, command, console
from ...libs import db, paths

__all__ = ["drop"]


@command("drop")
def drop(
    buckets: Annotated[
        list[Any],
        typer.Argument(
            help="The IDs of your to-be-deleted save buckets.",
            show_default=False,
            parser=PARSERS["bucket"],
        ),
    ],
):
    """
    Delete save buckets.

    WARNING: There's no going back...
    """

    for context in cast(
        list[
            contextlib.AbstractContextManager[
                tuple[sqlalchemy.orm.Session, db.RyujinxSave]
            ]
        ],
        buckets,
    ):
        with context as (client, save):
            client.delete(save)
            shutil.rmtree(
                paths.SAVE_INSTANCE_DIR.format(id=save.id), ignore_errors=True
            )
            console.print(f"Deleted bucket '{save.id}'.")

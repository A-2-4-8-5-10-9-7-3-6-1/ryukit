import shutil
from typing import Annotated

import rich
import rich.live
import rich.status
import rich.tree
import sqlalchemy
import sqlalchemy.orm
import typer

from ...libs import db, paths
from .__context__ import command

__all__ = []


@command("drop")
def _(
    buckets: Annotated[
        list[int],
        typer.Argument(
            help="The IDs of your to-be-deleted save buckets.",
            show_default=False,
        ),
    ],
):
    """
    Delete save buckets.

    WARNING: There's no going back...
    """

    tree = rich.tree.Tree(
        rich.status.Status("Deleting buckets...", spinner="dots")
    )
    with rich.live.Live(tree, refresh_per_second=10):
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
                    paths.SAVE_INSTANCE_DIR.format(id=save.id),
                    ignore_errors=True,
                )
                tree.add(f"Deleted bucket '{save.id}'.")
        tree.label = "Buckets deleted."

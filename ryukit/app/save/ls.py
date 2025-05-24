from typing import Annotated

import rich
import rich.table
import sqlalchemy
import typer

from ... import utils
from ...app.save.__context__ import command, console
from ...libs import components, db


@command("ls")
def ls(
    wildcards: Annotated[
        bool, typer.Option(help="Use your own SQL wildcards for keywords.")
    ] = False,
    filter_by: Annotated[
        list[str] | None,
        typer.Argument(
            show_default=False, help="A search term for the command."
        ),
    ] = None,
):
    """
    List your save buckets.

    When keywords are provided, only save entries matching those keywords are listed.
    """

    filter_by = filter_by or []
    pad = "" if wildcards else "%"
    table = components.Table(
        rich.table.Column("ID", justify="center"),
        rich.table.Column("LABEL"),
        rich.table.Column("CREATED"),
        rich.table.Column("UPDATED"),
        rich.table.Column("LAST USED"),
        rich.table.Column("SIZE", justify="center"),
    )
    with db.client() as client:
        any(
            table.add_row(
                *map(
                    str,
                    (
                        save.id,
                        save.label,
                        save.created,
                        save.updated,
                        save.last_used or "Never",
                        f"{utils.megabytes(save.size):.1f}MB",
                    ),
                )
            )
            for save in client.scalars(
                sqlalchemy.select(db.RyujinxSave).where(
                    sqlalchemy.and_(
                        *(
                            sqlalchemy.or_(
                                *(
                                    attr.like(f"'{pad}' || {word} || '{pad}'")
                                    for attr in [
                                        db.RyujinxSave.created,
                                        db.RyujinxSave.updated,
                                        db.RyujinxSave.last_used,
                                        sqlalchemy.func.lower(
                                            db.RyujinxSave.label
                                        ),
                                    ]
                                )
                            )
                            for word in filter_by
                        )
                    )
                )
            )
        )
    console.print(table)

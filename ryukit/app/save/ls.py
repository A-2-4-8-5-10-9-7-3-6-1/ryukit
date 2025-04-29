import typing

import rich
import rich.table
import typer

from ...core import db, ui
from ...core.ui import console
from ...utils import calculator
from .__context__ import *

__all__ = []


@save.command(name="ls")
def _(
    wildcards: typing.Annotated[
        bool, typer.Option(help="Use your own SQL wildcards for keywords.")
    ] = False,
    filter_by: typing.Annotated[
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
    table = ui.Table(
        rich.table.Column("ID", justify="center", style="bold"),
        rich.table.Column("LABEL"),
        rich.table.Column("CREATED"),
        rich.table.Column("UPDATED"),
        rich.table.Column("LAST USED"),
        rich.table.Column("SIZE", justify="center"),
    )
    with db.connect() as conn:
        any(
            table.add_row(
                *map(
                    str,
                    (
                        row["id"],
                        row["label"],
                        row["created"],
                        row["updated"],
                        row["last_used"] or "[italic dim]Never...",
                        f"{calculator.megabytes(row["size"]):.1f}MB",
                    ),
                )
            )
            for row in map(
                lambda x: typing.cast(db.models.RyujinxSave, x),
                map(
                    dict,
                    conn.execute(
                        f"""
                        SELECT
                            *
                        FROM
                            ryujinx_saves
                        WHERE
                        {
                            "true"
                            if not filter_by
                            else "AND ".join(
                                f"""
                                (
                                    {
                                        "OR ".join(
                                            f"{key} LIKE '{pad}' || :t{i} || '{pad}'"
                                            for key in [
                                                "LOWER(label)",
                                                "created",
                                                "updated",
                                                "last_used"
                                            ]
                                        )
                                    }
                                )
                                """
                                for i, _ in enumerate(filter_by)
                            )
                        }
                        """,
                        {f"t{i}": word for i, word in enumerate(filter_by)},
                    ),
                ),
            )
        )
    console.print(table)

import sqlite3
import typing

import rich
import rich.table
import typer

from ...core import db, presentation
from ...utils import calculator, typer_builder

__all__ = ["typer_builder_args"]


def command(
    wildcards: typing.Annotated[
        bool, typer.Option(help="Use your own SQL wildcards for keywords.")
    ] = False,
    keywords: typing.Annotated[
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

    keywords = keywords or []
    pad = "" if wildcards else "%"
    table = presentation.theme(rich.table.Table)(
        presentation.theme(rich.table.Column)(
            "ID", justify="center", style="bold"
        ),
        presentation.theme(rich.table.Column)("LABEL"),
        presentation.theme(rich.table.Column)("CREATED"),
        presentation.theme(rich.table.Column)("UPDATED"),
        presentation.theme(rich.table.Column)("LAST USED"),
        presentation.theme(rich.table.Column)(
            "SIZE", justify="center", style="blue"
        ),
    )
    console = presentation.theme(rich.console.Console)()

    with db.theme(sqlite3.connect)("DATABASE") as conn:
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
                        if not keywords
                        else 
                        "AND ".join(
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
                            for i in range(len(keywords))
                        )
                    }
                    """,
                    {f"t{i}": word.lower() for i, word in enumerate(keywords)},
                ),
            ),
        ):
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

    console.print(table)


typer_builder_args: typer_builder.BuilderArgs = {"command": command}

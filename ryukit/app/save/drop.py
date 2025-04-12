import sqlite3
import typing

import typer

from ryukit.core import ui

from ...core import db
from ...helpers import typer_builder

__all__ = ["typer_builder_args"]


def command(
    ids: typing.Annotated[
        list[int],
        typer.Argument(
            metavar="ID...",
            help="IDs of to-be-deleted save buckets.",
            show_default=False,
        ),
    ],
):
    """Delete save buckets."""

    questionmarks = ", ".join("?" for _ in range(len(ids)))

    with db.theme_applier(sqlite3.connect)("DATABASE") as conn:
        deleted: int
        (deleted,) = conn.execute(
            f"""
            SELECT
                COUNT(*)
            FROM ryujinx_saves
            WHERE
                id IN ({questionmarks});
            """,
            ids,
        ).fetchone()

        conn.execute(
            f"""
            DELETE FROM ryujinx_saves
            WHERE
                id IN ({questionmarks});
            """,
            ids,
        )

        ...

    ui.console.print(f"Deleted {deleted} buckets.")


typer_builder_args: typer_builder.TyperBuilderArgs = {"command": command}

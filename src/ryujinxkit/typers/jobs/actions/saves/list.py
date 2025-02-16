"""
- dependency level 3.
"""

import collections.abc
import sqlite3

from .....database.connection import connect


def action(
    order: collections.abc.Sequence[tuple[str, str]] | None = None
) -> collections.abc.Generator[sqlite3.Cursor]:
    """
    List saves.

    :param order: The order in which to sort rows.
    """

    with connect() as connection:
        yield connection.execute(
            f"""
            SELECT 
                CAST(id AS TEXT),
                CAST(tag AS TEXT),
                CAST(strftime("%Y/%m/%d %H:%M", created) AS TEXT),
                CAST(strftime("%Y/%m/%d %H:%M", updated) AS TEXT),
                CAST(strftime("%Y/%m/%d %H:%M", used) AS TEXT),
                CAST(ROUND(size / (1024 * 1024.0), 2) AS TEXT) || "MB"
            FROM (
                SELECT id, tag, created, updated, used, size
                FROM saves
                {
                    f"ORDER BY {
                        ", ".join(
                            f"{col} {direction.upper()}"
                            for col, direction in order
                        )
                    }"
                    if order is not None
                    else ""
                }
            );
            """
        )

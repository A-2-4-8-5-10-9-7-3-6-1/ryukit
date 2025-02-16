"""
- dependency level 3.
"""

from .....database.configs import SAVE_TAG_DEFAULT
from .....database.connection import connect


def action(tag: str = SAVE_TAG_DEFAULT) -> int:
    """
    Create a save.

    :param tag: A tag for the save.
    """

    with connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO saves (tag)
            VALUES (?);
            """,
            [tag],
        )

        return cursor.lastrowid  # type: ignore

import typing

from .....services.sqlite3.configs import DEFAULT_SAVE_TAG
from .....services.sqlite3.connection import connect


def action(tag: str = DEFAULT_SAVE_TAG) -> int:
    """
    Create a save.

    :param tag: A tag for the save.
    """

    with connect() as connection:
        return typing.cast(
            int,
            connection.execute(
                """
                INSERT INTO saves (tag)
                VALUES (?);
                """,
                [tag],
            ).lastrowid,
        )

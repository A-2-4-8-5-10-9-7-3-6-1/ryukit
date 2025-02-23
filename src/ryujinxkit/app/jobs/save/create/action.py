import typing

from .....services.sqlite3.configs import DB_CONFIGS
from .....services.sqlite3.connection import connect


def action(tag: str = DB_CONFIGS["defaults"]["save_tag"]) -> int:
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

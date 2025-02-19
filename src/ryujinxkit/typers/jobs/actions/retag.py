from ....database.connection import connect


def action(id_: str, tag: str) -> bool:
    """
    Change a save's tagging.

    :param %id_%: The save's ID.
    :param tag: The save's new tag.

    :returns: Whether or not the operation was successful.
    """

    with connect() as connection:
        return (
            connection.execute(
                """
                UPDATE saves
                SET tag = ?, updated = datetime("now")
                WHERE id = ?;
                """,
                [tag, id_],
            ).rowcount
            != 0
        )

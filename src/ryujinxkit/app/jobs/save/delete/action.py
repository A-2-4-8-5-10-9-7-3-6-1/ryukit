import shutil

from .....core.fs.node import Node
from .....core.fs.resolver import resolver
from .....services.sqlite3.connection import connect


def action(id_: str) -> bool:
    """
    Delete a save.

    :param %id_%: Save's ID.

    :returns: Whether or not the operation was successful.
    """

    with connect() as connection:
        if (
            connection.execute(
                """
                DELETE FROM saves
                WHERE id = ?;
                """,
                [id_],
            ).rowcount
            == 0
        ):
            return False

    with resolver.cache_locked((Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)):
        if resolver[Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER].exists():
            shutil.rmtree(resolver[Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER])

    return True

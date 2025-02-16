"""
- dependency level 3.
"""

import shutil

from .....database.connection import connect
from .....file_access.resolver import resolver
from .....file_access.resolver_node import ResolverNode


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

    with resolver.cache_locked(
        (ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
    ):
        if resolver[ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER].exists():
            shutil.rmtree(
                path=resolver[ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER]
            )

    return True

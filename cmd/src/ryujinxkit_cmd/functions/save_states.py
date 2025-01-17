"""
Save-state management functions.

Dependency level: ?.
"""

from ..enums import FileNode
from ..session import Session

# =============================================================================

# -----------------------------------------------------------------------------


def create_save(tag: str | None) -> str:
    """
    Create a new save state.

    :param tag: Save-state's tag.

    :returns: ID of the save state.
    """

    Session.database_cursor.execute(
        "INSERT INTO saves (tag) VALUES (?)",
        (None if tag is None else tag.replace(" ", "-"),),
    )

    with Session.RESOLVER.cache_only(
        (
            FileNode.SAVE_COLLECTION,
            str(
                *Session.database_cursor.execute(
                    "SELECT id FROM saves ORDER BY created DESC"
                ).fetchone()
            ),
        )
    ):
        [
            Session.RESOLVER(id_=id_).mkdir(parents=True)
            for id_ in [
                FileNode.SYSTEM_SAVE,
                FileNode.USER_SAVE,
                FileNode.USER_SAVE_META,
            ]
        ]

        return Session.RESOLVER(id_=FileNode.SAVE_COLLECTION).name


# =============================================================================

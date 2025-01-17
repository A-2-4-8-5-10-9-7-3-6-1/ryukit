"""
Save-state management functions.

Dependency level: ?.
"""

from typing import Callable, Sequence

from rich.progress import Progress

from ..enums import FileNode, UseOperation
from ..session import Session

# =============================================================================


def use_save(id_: str, operation: UseOperation) -> None:
    """
    Perform an operation on a save state.

    :param %id_%: Save-state's ID as a string.
    :param operation: Operation to perform.
    """

    total: int = 0
    order: Callable[[Sequence], Sequence] = (
        reversed if operation == UseOperation.RESTORE else lambda x: x
    )

    with (
        Session.RESOLVER.cache_only((FileNode.SAVE_COLLECTION, id_)),
        Progress(transient=True) as progress,
    ):
        task_id = progress.add_task(
            description=(
                "[yellow]Restoring[/yellow]"
                if operation == UseOperation.RESTORE
                else "[yellow]Updating[/yellow]"
            ),
            total=3,
        )

        for paths in [
            (FileNode.USER_SIDE_SYSTEM_SAVE, FileNode.SYSTEM_SAVE),
            (FileNode.USER_SIDE_SAVE_META, FileNode.SAVE_META),
            (FileNode.USER_SIDE_SAVE, FileNode.USER_SAVE),
        ]:
            source, dest = map(Session.RESOLVER, order(paths))
            size = sum(
                path.stat().st_size
                for path in source.rglob(pattern="*")
                if not path.is_dir()
            )
            total += size

            if size == 0:
                progress.update(task_id=task_id, advance=1)

                continue

            [
                (
                    lambda path=path, dest_path=dest / path.relative_to(
                        source
                    ): [
                        dest_path.parent.mkdir(parents=True, exist_ok=True),
                        dest_path.write_bytes(data=path.read_bytes()),
                        progress.update(
                            task_id=task_id,
                            advance=path.stat().st_size / size,
                        ),
                    ]
                )()
                for path in source.rglob(pattern="*")
                if not path.is_dir()
            ]

    match operation:
        case UseOperation.UPDATE:
            Session.database_cursor.execute(
                """
                UPDATE saves
                SET updated = datetime("now"), size = ?
                WHERE id = ?;
                """,
                [total, id_],
            )

        case UseOperation.RESTORE:
            Session.database_cursor.execute(
                """
                UPDATE saves
                SET used = datetime("now")
                WHERE id = ?;
                """,
                [id_],
            )


# -----------------------------------------------------------------------------


def create_save(tag: str) -> str:
    """
    Create a new save state.

    **Notes**:
        - Format `tag` before passing it through.

    :param tag: Save-state's tag.

    :returns: ID of the save state.
    """

    Session.database_cursor.execute(
        """
            INSERT INTO saves (tag)
            VALUES (?);
        """,
        [tag],
    )

    with Session.RESOLVER.cache_only(
        (
            FileNode.SAVE_COLLECTION,
            str(
                *Session.database_cursor.execute(
                    """
                    SELECT id FROM saves
                    ORDER BY created DESC;
                    """
                ).fetchone()
            ),
        )
    ):
        [
            Session.RESOLVER(id_=id_).mkdir(parents=True)
            for id_ in [
                FileNode.USER_SIDE_SYSTEM_SAVE,
                FileNode.USER_SIDE_SAVE,
                FileNode.USER_SIDE_SAVE_META,
            ]
        ]

        [
            (
                Session.RESOLVER(id_=FileNode.USER_SIDE_SYSTEM_SAVE) / str(i)
            ).write_text(data=str(i))
            for i in range(100)
        ]

        return Session.RESOLVER(id_=FileNode.SAVE_COLLECTION).name


# =============================================================================

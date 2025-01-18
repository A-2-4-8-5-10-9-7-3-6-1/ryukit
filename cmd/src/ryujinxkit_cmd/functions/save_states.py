"""
Save-state management functions.

Dependency level: 2.
"""

from pathlib import Path
from sqlite3 import connect
from tarfile import TarFile
from tempfile import TemporaryDirectory
from time import sleep
from typing import Callable, Sequence

from rich.progress import Progress

from ..constants.configs import DATABASE_INSERT_BUFFER
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
                progress.advance(task_id=task_id, advance=1)

                continue

            [
                (
                    lambda path=path, dest_path=dest / path.relative_to(
                        source
                    ): [
                        dest_path.parent.mkdir(parents=True, exist_ok=True),
                        dest_path.write_bytes(data=path.read_bytes()),
                        progress.advance(
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

    sleep(DATABASE_INSERT_BUFFER)

    with Session.RESOLVER.cache_only(
        (FileNode.SAVE_COLLECTION, str(Session.database_cursor.lastrowid))
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

        return Session.database_cursor.lastrowid


# -----------------------------------------------------------------------------


def archive(output: str) -> None:
    """
    Archive all save states into a tar file.

    :param output: A title for the tar file.
    """

    with (
        TarFile(name=output, mode="w") as tar,
        Progress(transient=True) as progress,
    ):
        task_id = progress.add_task(
            description="[yellow]Archiving[/yellow]",
            total=Session.database_cursor.execute(
                """
                SELECT COUNT(*)
                FROM saves;
                """
            ).fetchone()[0],
        )

        tar.add(
            name=Session.RESOLVER(id_=FileNode.DATABASE),
            arcname=Session.RESOLVER(id_=FileNode.DATABASE).name,
        )

        for id_, size in Session.database_cursor.execute(
            """
            SELECT CAST(id AS TEXT), size 
            FROM saves
            """
        ).fetchall():
            with Session.RESOLVER.cache_only((FileNode.SAVE_COLLECTION, id_)):
                [
                    [
                        tar.add(
                            name=path,
                            arcname=path.relative_to(
                                Session.RESOLVER(id_=FileNode.APP_DATA)
                            ),
                        ),
                        (
                            progress.advance(
                                task_id=task_id,
                                advance=path.stat().st_size / size,
                            )
                            if not path.is_dir()
                            else None
                        ),
                    ]
                    for path in Session.RESOLVER(
                        id_=FileNode.SAVE_COLLECTION
                    ).rglob(pattern="*")
                ]


# -----------------------------------------------------------------------------


def read_archive(path: Path) -> int:
    """
    Assimilate save states from an archive.

    :param path: Path to your archive.

    :returns: Number of read save states.
    """

    with (
        TemporaryDirectory() as temp_dir,
        TarFile(name=path, stream=True) as tar,
        Progress(transient=True) as progress,
    ):
        temp_dir = Path(temp_dir)
        task_id = progress.add_task(
            description="[yellow]Extracting[/yellow]",
            total=0,
        )

        [
            [
                tar.extract(member=member, path=temp_dir),
                progress.advance(task_id=task_id, advance=member.size),
            ]
            for member in [
                [
                    member,
                    (
                        progress.update(
                            task_id=task_id,
                            total=progress.tasks[0].total + member.size,
                        )
                        if not member.isdir()
                        else None
                    ),
                ][0]
                for member in tar
            ]
        ]

        progress.update(
            task_id=task_id,
            description="[green]Extracted[/green]",
        )

        cursor = connect(
            database=temp_dir
            / Session.RESOLVER(id_=FileNode.DATABASE).relative_to(
                Session.RESOLVER(id_=FileNode.APP_DATA)
            )
        ).cursor()
        states = cursor.execute(
            """
            SELECT CAST(id AS TEXT), tag, created, updated, used, size
            FROM saves;
            """
        ).fetchall()
        task_id = progress.add_task(
            description="[yellow]Reading[/yellow]",
            total=len(states),
        )

        for id_, *attrs, size in states:
            save_dir = (
                temp_dir
                / Session.RESOLVER(id_=FileNode.SAVE_FOLDER).name
                / id_
            )

            Session.database_cursor.execute(
                """
                INSERT INTO saves
                    (tag, created, updated, used, size)
                VALUES (?, ?, ?, ?, ?);
                """,
                (*attrs, size),
            )

            sleep(DATABASE_INSERT_BUFFER)

            with Session.RESOLVER.cache_only(
                (
                    FileNode.SAVE_COLLECTION,
                    str(Session.database_cursor.lastrowid),
                )
            ):
                [
                    (
                        lambda subpath: (
                            [
                                subpath.write_bytes(data=entry.read_bytes()),
                                progress.advance(
                                    task_id=task_id,
                                    advance=subpath.stat().st_size / size,
                                ),
                            ]
                            if not entry.is_dir()
                            else subpath.mkdir(parents=True, exist_ok=True)
                        )
                    )(
                        Session.RESOLVER(id_=FileNode.SAVE_COLLECTION)
                        / entry.relative_to(save_dir)
                    )
                    for entry in save_dir.rglob(pattern="*")
                ]

                if size == 0:
                    progress.advance(task_id=task_id, advance=1)


# =============================================================================

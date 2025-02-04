"""
- dependency level 0.
"""

from io import BytesIO
from json import dumps, loads
from pathlib import Path
from shutil import rmtree
from tarfile import TarFile, TarInfo
from tempfile import TemporaryDirectory
from typing import Any, Callable, Iterable, Literal, Sequence

from rich.console import Console
from rich.progress import Progress

from ryujinxkit.general import FileNode, Session

# =============================================================================


def use_save(
    console: Console,
    id_: str,
    operation: Literal["restore", "update"],
) -> None:
    """
    Perform an operation on a save state.

    :param console: A console to track progress on.
    :param %id_%: Save-state's ID as a string.
    :param operation: Usage operation.
    """

    total: int = 0
    initial_size = Session.database_cursor.execute(
        """
        SELECT size
        FROM saves
        WHERE id = ?;
        """,
        [id_],
    ).fetchone()[0]
    final_query: Callable[[int], tuple[str, list[Any]]]
    order: Callable[[Sequence[FileNode]], Sequence[FileNode]]
    size_logic: Callable[[Iterable[Path]], int]

    match operation:
        case "restore":
            order = lambda x: x
            size_logic = lambda _: initial_size
            final_query = lambda _: (
                """
                UPDATE saves
                SET used = datetime("now")
                WHERE id = ?;
                """,
                [id_],
            )

        case "update":
            order = reversed
            size_logic = lambda members: sum(
                path.stat().st_size for path in members
            )
            final_query = lambda total: (
                """
                UPDATE saves
                SET updated = datetime("now"), size = ?
                WHERE id = ?;
                """,
                [total, id_],
            )

    with (
        Session.resolver.cache_only(
            (FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
        ),
        Progress(transient=True, console=console) as progress,
    ):
        task_id = progress.add_task(
            description=(f"[yellow]{operation.title()[:-1]}ing[/yellow]"),
            total=3,
        )

        for paths in [
            (
                FileNode.RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE,
                FileNode.RYUJINX_SYSTEM_SAVE,
            ),
            (
                FileNode.RYUJINXKIT_SAVE_INSTANCE_SAVE_META,
                FileNode.RYUJINX_SAVE_META,
            ),
            (
                FileNode.RYUJINXKIT_SAVE_INSTANCE_SAVE,
                FileNode.RYUJINX_USER_SAVE,
            ),
        ]:
            source, dest = map(Session.resolver, order(paths))
            members = [
                path for path in source.rglob(pattern="*") if not path.is_dir()
            ]
            size = size_logic(members)
            total += size

            if dest.exists():
                rmtree(path=dest)

            if size == 0:
                progress.advance(task_id=task_id, advance=1)

                continue

            [
                (
                    lambda path, dest: [
                        dest.parent.mkdir(parents=True, exist_ok=True),
                        dest.write_bytes(data=path.read_bytes()),
                        progress.advance(
                            task_id=task_id,
                            advance=path.stat().st_size / size,
                        ),
                    ]
                )(path, dest / path.relative_to(source))
                for path in members
            ]

    Session.database_cursor.execute(*final_query(total))


# -----------------------------------------------------------------------------


def remove_save(console: Console, id_: str) -> None:
    """
    Removes a save state.

    :param %id_%: ID of save state.
    :param console: A console to track progress on.
    """

    with Session.resolver.cache_only(
        (FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
    ):
        if Session.resolver(
            id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
        ).exists():
            with Progress(transient=True, console=console) as progress:
                task_id = progress.add_task(
                    description="[yellow]Deleting[/yellow]",
                    total=Session.database_cursor.execute(
                        """
                        SELECT size
                        FROM saves
                        WHERE id = ?;
                        """,
                        [id_],
                    ).fetchone()[0],
                )

                [
                    progress.advance(
                        task_id=task_id,
                        advance=[path.stat().st_size, path.unlink()][0],
                    )
                    for path in Session.resolver(
                        id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                    ).rglob(pattern="*")
                    if not path.is_dir()
                ]

            rmtree(
                path=Session.resolver(
                    id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                )
            )

    Session.database_cursor.execute(
        """
        DELETE FROM saves
        WHERE id = ?;
        """,
        [id_],
    )


# -----------------------------------------------------------------------------


def archive(console: Console, output: str) -> None:
    """
    Archive all save states into a tar file.

    :param output: Output's file-path.
    :param console: A console to track progress on.
    """

    with (
        TarFile(name=output, mode="w") as tar,
        Progress(transient=True, console=console) as progress,
        BytesIO() as buffer,
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
        entities_info = TarInfo(name="entities.json")
        entities_info.size = buffer.write(
            dumps(
                obj=[
                    dict(
                        zip(
                            (
                                "id",
                                "tag",
                                "created",
                                "updated",
                                "used",
                                "size",
                            ),
                            record,
                        )
                    )
                    for record in Session.database_cursor.execute(
                        """
                        SELECT id, tag, created, updated, used, size
                        FROM saves;
                        """
                    ).fetchall()
                ]
            ).encode()
        )

        buffer.seek(0)

        tar.addfile(tarinfo=entities_info, fileobj=buffer)

        for id_, size in Session.database_cursor.execute(
            """
            SELECT CAST(id AS TEXT), size
            FROM saves;
            """
        ).fetchall():
            with Session.resolver.cache_only(
                (FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
            ):
                [
                    [
                        tar.add(
                            name=path,
                            arcname=path.relative_to(
                                Session.resolver(
                                    id_=FileNode.RYUJINXKIT_ROAMING_DATA
                                )
                            ),
                        ),
                        progress.advance(
                            task_id=task_id,
                            advance=path.stat().st_size / size,
                        ),
                    ]
                    for path in Session.resolver(
                        id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                    ).rglob(pattern="*")
                    if not path.is_dir()
                ]


# -----------------------------------------------------------------------------


def read_archive(console: Console, path: Path) -> int:
    """
    Assimilate save states from an archive.

    :param path: Path to your archive.
    :param console: A console to track progress on.

    :returns: Number of read save states.
    """

    with (
        TemporaryDirectory() as temp_dir,
        TarFile(name=path, stream=True) as tar,
        Progress(transient=True, console=console) as progress,
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

        states: Iterable[dict[str, Any]] = loads(
            s=(temp_dir / "entities.json").read_bytes()
        )
        task_id = progress.add_task(
            description="[yellow]Reading[/yellow]",
            total=len(states),
        )

        for state in states:
            save_dir = (
                temp_dir
                / Session.resolver(id_=FileNode.RYUJINXKIT_SAVE_FOLDER).name
                / str(state["id"])
            )

            Session.database_cursor.execute(
                """
                INSERT INTO saves (tag, created, updated, used, size)
                VALUES (?, ?, ?, ?, ?);
                """,
                list(
                    map(
                        state.__getitem__,
                        ("tag", "created", "updated", "used", "size"),
                    )
                ),
            )

            with Session.resolver.cache_only(
                (
                    FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
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
                                    advance=subpath.stat().st_size
                                    / state["size"],
                                ),
                            ]
                            if not entry.is_dir()
                            else subpath.mkdir(parents=True, exist_ok=True)
                        )
                    )(
                        Session.resolver(
                            id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                        )
                        / entry.relative_to(save_dir)
                    )
                    for entry in save_dir.rglob(pattern="*")
                ]

                if state["size"] == 0:
                    progress.advance(task_id=task_id, advance=1)

        return len(states)


# =============================================================================

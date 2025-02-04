"""
- dependency level 0.
"""

from io import BytesIO
from json import dumps, load
from pathlib import Path
from shutil import rmtree
from tarfile import TarFile, TarInfo
from tempfile import TemporaryDirectory
from typing import Any, Callable, Iterable, Literal, Sequence

from rich.console import Console
from rich.progress import Progress, SpinnerColumn

from ryujinxkit.general import UI_REFRESH_RATE, FileNode, Session

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
        Progress(
            SpinnerColumn(style="dim"),
            "[dim]{task.description}",
            "[dim]({task.completed}/{task.total})",
            console=console,
            refresh_per_second=UI_REFRESH_RATE,
            transient=True,
        ) as progress,
    ):
        paths = [
            map(Session.resolver, pair)
            for pair in map(
                order,
                [
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
                ],
            )
        ]
        task_id = progress.add_task(
            description="Copying files",
            total=len(paths),
        )

        for source, dest in paths:
            members = [
                path for path in source.rglob(pattern="*") if not path.is_dir()
            ]
            size = size_logic(members)
            total += size

            if dest.exists():
                rmtree(path=dest)

            if size != 0:
                [
                    (
                        lambda path, dest: [
                            dest.parent.mkdir(parents=True, exist_ok=True),
                            dest.write_bytes(data=path.read_bytes()),
                        ]
                    )(path, dest / path.relative_to(source))
                    for path in members
                ]

            progress.advance(task_id=task_id, advance=1)

    Session.database_cursor.execute(*final_query(total))


# -----------------------------------------------------------------------------


def remove_save(console: Console, id_: str) -> None:
    """
    Removes a save state.

    :param %id_%: ID of save state.
    :param console: A console to track progress on.
    """

    with (
        Session.resolver.cache_only(
            (FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
        ),
        console.status(
            status="[dim]Deleting save",
            spinner_style="dim",
            refresh_per_second=UI_REFRESH_RATE,
        ),
    ):
        Session.database_cursor.execute(
            """
            DELETE FROM saves
            WHERE id = ?;
            """,
            [id_],
        )

        if Session.resolver(
            id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
        ).exists():
            rmtree(
                path=Session.resolver(
                    id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                )
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
        Progress(
            SpinnerColumn(style="dim"),
            "[dim]{task.description}",
            "[dim]({task.percentage:.1f}%)",
            console=console,
            refresh_per_second=UI_REFRESH_RATE,
            transient=True,
        ) as progress,
    ):
        task_id = progress.add_task(
            description="Exporting",
            total=Session.database_cursor.execute(
                """
                SELECT COUNT(*)
                FROM saves;
                """
            ).fetchone()[0],
        )
        entities_info = TarInfo(name="entities.json")

        with BytesIO() as buffer:
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
                if not Session.resolver(
                    id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                ).exists():
                    progress.advance(task_id=task_id, advance=1)

                    continue
                [
                    [
                        tar.add(
                            name=path,
                            arcname=str(
                                path.relative_to(
                                    Session.resolver(
                                        id_=FileNode.RYUJINXKIT_ROAMING_DATA
                                    )
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
    ):
        temp_dir = Path(temp_dir)
        states: Iterable[dict[str, Any]]

        with console.status(
            status="Extracting export",
            spinner_style="dim",
            refresh_per_second=UI_REFRESH_RATE,
        ) as progress:
            tar.extractall(path=temp_dir)

        with (temp_dir / "entities.json").open() as buffer:
            states = load(fp=buffer)

        with Progress(
            SpinnerColumn(style="dim"),
            "[dim]{task.description}",
            "[dim]({task.percentage:.1f}%)",
            console=console,
            refresh_per_second=UI_REFRESH_RATE,
            transient=True,
        ) as progress:
            task_id = progress.add_task(
                description="Reading export",
                total=len(states),
            )

            for state in states:
                save_dir = (
                    temp_dir
                    / Session.resolver(
                        id_=FileNode.RYUJINXKIT_SAVE_FOLDER
                    ).name
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

                if state["size"] == 0:
                    progress.advance(task_id=task_id, advance=1)

                    continue

                with Session.resolver.cache_only(
                    (
                        FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                        str(Session.database_cursor.lastrowid),
                    )
                ):
                    for entry in save_dir.rglob(pattern="*"):
                        subpath = Session.resolver(
                            id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                        ) / entry.relative_to(save_dir)

                        if entry.is_dir():
                            subpath.mkdir(parents=True, exist_ok=True)

                            continue

                        subpath.write_bytes(data=entry.read_bytes())

                        progress.advance(
                            task_id=task_id,
                            advance=subpath.stat().st_size / state["size"],
                        )

        return len(states)


# =============================================================================

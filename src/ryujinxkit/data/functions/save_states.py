"""
- dependency level 1.
"""

from io import BytesIO
from json import dumps, load
from pathlib import Path
from shutil import rmtree
from sqlite3 import Cursor
from tarfile import TarFile, TarInfo
from tempfile import TemporaryDirectory
from typing import Any, Callable, Iterable, Literal, Sequence

from rich.console import Console
from rich.progress import Progress, SpinnerColumn

from ryujinxkit.general import (
    DATABASE_SAVE_TAG_DEFAULT,
    UI_REFRESH_RATE,
    FileNode,
    Session,
    apply_formatters,
    format_tag,
)

from ..constants.configs import DEFAULT_ARCHIVE_NAME

# =============================================================================


@apply_formatters(formatters=[("tag", format_tag)])
def create_save(tag: str = DATABASE_SAVE_TAG_DEFAULT) -> None:
    """
    Create a new save.

    :param tag: A tag for the save.
    """

    Session.database_cursor.execute(
        """
        INSERT INTO saves (tag)
        VALUES (?);
        """,
        [tag],
    )


# -----------------------------------------------------------------------------


@apply_formatters(formatters=[("tag", format_tag)])
def retag_save(id_: str, tag: str) -> None:
    """
    Change a save's tagging.

    :param %id_%: The save's ID.
    :param tag: The save's new tag.
    """

    Session.database_cursor.execute(
        """
        UPDATE saves
        SET tag = ?, updated = datetime("now")
        WHERE id = ?;
        """,
        [tag, id_],
    )


# -----------------------------------------------------------------------------


def collect_saves(
    order_by: Sequence[
        Literal[
            "id+",
            "tag+",
            "created+",
            "updated+",
            "used+",
            "size+",
            "id-",
            "tag-",
            "created-",
            "updated-",
            "used-",
            "size-",
        ]
    ]
) -> Cursor:
    """
    Collect complete list of save states into a `sqlite3.Cursor`.

    :param order_by: How you want the results ordered.

    :returns: `sqlite3.Cursor` containing results.
    """

    return Session.database_cursor.execute(
        f"""
        SELECT 
            CAST(id AS TEXT),
            CAST(tag AS TEXT),
            CAST(strftime("%Y/%m/%d %H:%M", created) AS TEXT),
            CAST(strftime("%Y/%m/%d %H:%M", updated) AS TEXT),
            CAST(strftime("%Y/%m/%d %H:%M", used) AS TEXT),
            CAST(ROUND(size / (1024 * 1024.0), 2) AS TEXT) || "MB"
        FROM (
            SELECT id, tag, created, updated, used, size
            FROM saves
            ORDER BY {
                ", ".join(
                    f"{flag[:-1]} {"DESC" if flag[-1] == "-" else "ASC"}"
                    for flag in order_by
                )
            }
        )
        """
    )


# -----------------------------------------------------------------------------


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


@apply_formatters(
    formatters=[("output", lambda x: x if x != "" else DEFAULT_ARCHIVE_NAME)]
)
def archive(console: Console, output: str) -> None:
    """
    Archive all save states into a tar file.

    :param output: Output's file-path.
    :param console: A console to track progress on.
    """

    with (
        TarFile(name=output, mode="w") as tar,
        console.status(
            status="[dim]Exporting saves",
            spinner_style="dim",
            refresh_per_second=UI_REFRESH_RATE,
        ),
    ):
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
                        )
                    ]
                ).encode()
            )

            buffer.seek(0)

            tar.addfile(tarinfo=entities_info, fileobj=buffer)

        for (id_,) in Session.database_cursor.execute(
            """
            SELECT CAST(id AS TEXT)
            FROM saves;
            """
        ):
            with Session.resolver.cache_only(
                (FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
            ):
                if not Session.resolver(
                    id_=FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                ).exists():
                    continue

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
                    )
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
        ):
            tar.extractall(path=temp_dir)

        with (temp_dir / "entities.json").open() as buffer:
            states = load(fp=buffer)

        state_count = len(states)

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
                total=state_count,
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
                            ["tag", "created", "updated", "used", "size"],
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

        return state_count


# =============================================================================

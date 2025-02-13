"""
- dependency level 1.
"""

import collections.abc
import io
import json
import pathlib
import shutil
import sqlite3
import tarfile
import tempfile
import typing

import rich.console
import rich.progress

import ryujinxkit.general

from ..formatting.formatters import format_tag


@ryujinxkit.general.apply_formatters
def create_save(
    tag: typing.Annotated[
        str,
        ryujinxkit.general.Formatter(function=format_tag),
    ] = ryujinxkit.general.DATABASE_SAVE_TAG_DEFAULT,
) -> None:
    """
    Create a new save.

    :param tag: A tag for the save.
    """

    ryujinxkit.general.Session.database_cursor.execute(
        """
        INSERT INTO saves (tag)
        VALUES (?);
        """,
        [tag],
    )


@ryujinxkit.general.apply_formatters
def retag_save(
    id_: str,
    tag: typing.Annotated[
        str,
        ryujinxkit.general.Formatter(function=format_tag),
    ],
) -> None:
    """
    Change a save's tagging.

    :param %id_%: The save's ID.
    :param tag: The save's new tag.
    """

    ryujinxkit.general.Session.database_cursor.execute(
        """
        UPDATE saves
        SET tag = ?, updated = datetime("now")
        WHERE id = ?;
        """,
        [tag, id_],
    )


def collect_saves(
    console: rich.console.Console,
    order_by: collections.abc.Sequence[
        typing.Literal[
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
    ],
) -> sqlite3.Cursor:
    """
    Collect complete list of save states into a `sqlite3.sqlite3.Cursor`.

    :param console: rich.console.Console for logging progress.
    :param order_by: How you want the results ordered.

    :returns: `sqlite3.sqlite3.Cursor` containing results.
    """
    with console.status(
        status="[dim]Collecting saves",
        spinner_style="dim",
        refresh_per_second=ryujinxkit.general.UI_REFRESH_RATE,
    ):
        return ryujinxkit.general.Session.database_cursor.execute(
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


def use_save(
    console: rich.console.Console,
    id_: str,
    operation: typing.Literal["restore", "update"],
) -> None:
    """
    Perform an operation on a save state.

    :param console: A console to track progress on.
    :param %id_%: Save-state's ID as a string.
    :param operation: Usage operation.
    """

    total: int = 0
    initial_size = ryujinxkit.general.Session.database_cursor.execute(
        """
        SELECT size
        FROM saves
        WHERE id = ?;
        """,
        [id_],
    ).fetchone()[0]
    final_query: collections.abc.Callable[[int], tuple[str, list[typing.Any]]]
    order: collections.abc.Callable[
        [collections.abc.Sequence[ryujinxkit.general.FileNode]],
        collections.abc.Iterable[ryujinxkit.general.FileNode],
    ]
    size_logic: collections.abc.Callable[
        [collections.abc.Iterable[pathlib.Path]],
        int,
    ]

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
        ryujinxkit.general.Session.resolver.cache_locked(
            (ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
        ),
        rich.progress.Progress(
            rich.progress.SpinnerColumn(style="dim"),
            "[dim]{task.description}",
            "[dim]({task.completed}/{task.total})",
            console=console,
            refresh_per_second=ryujinxkit.general.UI_REFRESH_RATE,
            transient=True,
        ) as progress,
    ):
        paths = [
            map(ryujinxkit.general.Session.resolver, pair)
            for pair in map(
                order,
                [
                    (
                        ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE,
                        ryujinxkit.general.FileNode.RYUJINX_SYSTEM_SAVE,
                    ),
                    (
                        ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_SAVE_META,
                        ryujinxkit.general.FileNode.RYUJINX_SAVE_META,
                    ),
                    (
                        ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_SAVE,
                        ryujinxkit.general.FileNode.RYUJINX_USER_SAVE,
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
                shutil.rmtree(path=dest)

            if size != 0:
                for path in members:
                    bucket = dest / path.relative_to(source)

                    bucket.parent.mkdir(parents=True, exist_ok=True)
                    bucket.write_bytes(data=path.read_bytes())

            progress.advance(task_id=task_id, advance=1)

    ryujinxkit.general.Session.database_cursor.execute(*final_query(total))


def remove_save(console: rich.console.Console, id_: str) -> None:
    """
    Removes a save state.

    :param %id_%: ID of save state.
    :param console: A console to track progress on.
    """

    with (
        ryujinxkit.general.Session.resolver.cache_locked(
            (ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
        ),
        console.status(
            status="[dim]Deleting save",
            spinner_style="dim",
            refresh_per_second=ryujinxkit.general.UI_REFRESH_RATE,
        ),
    ):
        ryujinxkit.general.Session.database_cursor.execute(
            """
            DELETE FROM saves
            WHERE id = ?;
            """,
            [id_],
        )

        if ryujinxkit.general.Session.resolver(
            id_=ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
        ).exists():
            shutil.rmtree(
                path=ryujinxkit.general.Session.resolver(
                    id_=ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                )
            )


def archive(console: rich.console.Console, output: pathlib.Path) -> None:
    """
    Archive all save states into a tar file.

    :param output: Output's file-path.
    :param console: A console to track progress on.
    """

    with (
        tarfile.TarFile(name=output, mode="w") as tar,
        console.status(
            status="[dim]Exporting saves",
            spinner_style="dim",
            refresh_per_second=ryujinxkit.general.UI_REFRESH_RATE,
        ),
    ):
        entities_info = tarfile.TarInfo(name="entities.json")

        with io.BytesIO() as buffer:
            entities_info.size = buffer.write(
                json.dumps(
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
                        for record in ryujinxkit.general.Session.database_cursor.execute(
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

        for (id_,) in ryujinxkit.general.Session.database_cursor.execute(
            """
            SELECT CAST(id AS TEXT)
            FROM saves;
            """
        ):
            with ryujinxkit.general.Session.resolver.cache_locked(
                (
                    ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                    id_,
                )
            ):
                if not ryujinxkit.general.Session.resolver(
                    id_=ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                ).exists():
                    continue

                [
                    tar.add(
                        name=path,
                        arcname=str(
                            path.relative_to(
                                ryujinxkit.general.Session.resolver(
                                    id_=ryujinxkit.general.FileNode.RYUJINXKIT_ROAMING_DATA
                                )
                            )
                        ),
                    )
                    for path in ryujinxkit.general.Session.resolver(
                        id_=ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                    ).rglob(pattern="*")
                    if not path.is_dir()
                ]


def read_archive(console: rich.console.Console, path: pathlib.Path) -> int:
    """
    Assimilate save states from an archive.

    :param path: pathlib.Path to your archive.
    :param console: A console to track progress on.

    :returns: Number of read save states.
    """

    with (
        tempfile.TemporaryDirectory() as temp_dir,
        tarfile.TarFile(name=path, stream=True) as tar,
    ):
        temp_dir = pathlib.Path(temp_dir)
        states: collections.abc.Sequence[dict[str, typing.Any]]

        with console.status(
            status="Extracting export",
            spinner_style="dim",
            refresh_per_second=ryujinxkit.general.UI_REFRESH_RATE,
        ):
            tar.extractall(path=temp_dir)

        with (temp_dir / "entities.json").open() as buffer:
            states = json.load(fp=buffer)

        state_count = len(states)

        with rich.progress.Progress(
            rich.progress.SpinnerColumn(style="dim"),
            "[dim]{task.description}",
            "[dim]({task.percentage:.1f}%)",
            console=console,
            refresh_per_second=ryujinxkit.general.UI_REFRESH_RATE,
            transient=True,
        ) as progress:
            task_id = progress.add_task(
                description="Reading export",
                total=state_count,
            )

            for state in states:
                save_dir = (
                    temp_dir
                    / ryujinxkit.general.Session.resolver(
                        id_=ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_FOLDER
                    ).name
                    / str(state["id"])
                )

                ryujinxkit.general.Session.database_cursor.execute(
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

                with ryujinxkit.general.Session.resolver.cache_locked(
                    (
                        ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                        str(
                            ryujinxkit.general.Session.database_cursor.lastrowid
                        ),
                    )
                ):
                    for entry in save_dir.rglob(pattern="*"):
                        subpath = ryujinxkit.general.Session.resolver(
                            id_=ryujinxkit.general.FileNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
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

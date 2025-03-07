import collections.abc
import datetime
import enum
import json
import pathlib
import tarfile
import tempfile
import typing

import rich.progress
import rich.status
import rich.table

from ....core.fs.node import Node
from ....core.fs.resolver import resolver
from ....core.ui.configs import UI_CONFIGS
from ....core.ui.console import console
from ....services.sqlite3.connection import connect
from ...context import settings
from ..merger import merger
from ..signals import Primer

__all__ = ["extract_command"]


class ExtractSignal(int, enum.Enum):
    EXTRACTING = 0
    FAILED = 1
    READING = 2


def presenter() -> (
    collections.abc.Generator[None, tuple[ExtractSignal, float] | Primer]
):
    looping = False
    animation: rich.progress.Progress | rich.status.Status | None = None
    task_id: rich.progress.TaskID | None = None
    r_total: float | None = None

    while True:
        match (yield):
            case ExtractSignal.EXTRACTING, 0:
                animation = console.status(
                    status="Extracting",
                    spinner_style="dim",
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
                )

                animation.start()

            case ExtractSignal.FAILED, 0:
                looping = False

                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={"code": "EXTRACTION_ISSUE"}
                    )

                return console.print("Malformed export file.")

            case ExtractSignal.READING, volume:
                if looping:
                    animation = typing.cast(
                        rich.progress.Progress, animation
                    ).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                typing.cast(rich.status.Status, animation).stop()

                animation = rich.progress.Progress(
                    rich.progress.SpinnerColumn(style="dim"),
                    "[dim]{task.description}",
                    "[dim]({task.percentage:.1f}%)",
                    console=console,
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
                    transient=True,
                )
                task_id = animation.add_task(
                    description="Reading", total=volume
                )
                r_total = volume
                looping = True

                animation.start()

            case Primer.FINISHED:
                looping = False
                r_total = typing.cast(int, r_total)

                typing.cast(rich.progress.Progress, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={"code": "SUCCESS", "accepted": r_total}
                    )

                return console.print(f"Accepted {r_total} save instance(s).")

            case Primer.KILL:
                if animation is not None:
                    animation.stop()

                return

            case _:
                pass


def action(
    path: pathlib.Path,
) -> collections.abc.Generator[tuple[ExtractSignal, float]]:
    """
    Extract saves from an export.

    :param path: Path to your export.

    :returns: Signal generator for extract command.
    """

    class SaveEntity(typing.TypedDict):
        tag: str
        created: datetime.date
        updated: datetime.date
        used: datetime.date
        size: int
        id: int

    try:
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            tarfile.TarFile(name=path, stream=True) as tar,
        ):
            temp_dir = pathlib.Path(temp_dir)

            yield (ExtractSignal.EXTRACTING, 0)

            tar.extractall(temp_dir)

            with (temp_dir / "entities.json").open() as buffer:
                entities: collections.abc.Sequence[SaveEntity] = json.load(
                    buffer
                )

            yield (ExtractSignal.READING, len(entities))

            with connect() as connection:
                for entity in entities:
                    save_dir = (
                        temp_dir
                        / resolver[Node.RYUJINXKIT_SAVE_FOLDER].name
                        / str(entity["id"])
                    )

                    connection.execute(
                        """
                        INSERT INTO saves (tag, created, updated, used, size)
                        VALUES (:tag, :created, :updated, :used, :size);
                        """,
                        entity,
                    )

                    if entity["size"] == 0:
                        yield (ExtractSignal.READING, 1)

                        continue

                    with resolver.cache_locked(
                        (
                            Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                            str(connection.cursor().lastrowid),
                        )
                    ):
                        for entry in save_dir.rglob("*"):
                            subpath = resolver[
                                Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                            ] / entry.relative_to(save_dir)

                            if entry.is_dir():
                                subpath.mkdir(parents=True, exist_ok=True)

                                continue

                            subpath.write_bytes(entry.read_bytes())

                            yield (
                                ExtractSignal.READING,
                                subpath.stat().st_size / entity["size"],
                            )

    except Exception:
        yield (ExtractSignal.FAILED, 0)


@merger(action=action, presenter=presenter)
def extract_command(
    in_: collections.abc.Generator[tuple[ExtractSignal, float]],
    pole: collections.abc.Generator[
        None, tuple[ExtractSignal, float] | Primer
    ],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == ExtractSignal.FAILED:
            return

    pole.send(Primer.FINISHED)

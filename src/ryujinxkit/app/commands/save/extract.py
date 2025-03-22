"""Save-extract command.

Exports
-------
- :func:`save_extract_command`: The save-extract command.
"""

import collections
import collections.abc
import enum
import json
import pathlib
import tarfile
import tempfile
import typing

import rich
import rich.progress
import rich.status
import rich.table

from ....core.db.connection import connect
from ....core.db.models.save import Save
from ....core.fs.resolver import Node, resolver
from ....core.ui.objects import console
from ....core.ui.styling import styled
from ...context import settings
from ..AP_decomp import PrimitiveSignal, merger


class ExtractSignal(int, enum.Enum):
    EXTRACTING = 0
    FAILED = 1
    READING = 2


def presentation() -> (
    collections.abc.Generator[
        None, tuple[ExtractSignal, float] | PrimitiveSignal
    ]
):
    looping = False
    animation: rich.progress.Progress | rich.status.Status | None = None
    task_id: rich.progress.TaskID | None = None
    r_total: float | None = None

    while True:
        match (yield):
            case ExtractSignal.EXTRACTING, 0:
                animation = styled(rich.status.Status)(status="Extracting...")

                animation.start()

            case ExtractSignal.FAILED, 0:
                looping = False

                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={"code": "EXTRACTION_ISSUE"}
                    )

                return console.print("Malformed export file.", style="error")

            case ExtractSignal.READING, volume:
                if looping:
                    typing.cast(rich.progress.Progress, animation).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                typing.cast(rich.status.Status, animation).stop()

                animation = styled(rich.progress.Progress)(
                    styled(rich.progress.SpinnerColumn)(),
                    "{task.description}",
                    "({task.percentage:.1f}%)",
                )
                task_id = animation.add_task(
                    description="Reading entities...", total=volume
                )
                r_total = volume
                looping = True

                animation.start()

            case PrimitiveSignal.FINISHED:
                looping = False
                r_total = typing.cast(int, r_total)
                animation = typing.cast(rich.progress.Progress, animation)

                animation.update(
                    task_id=typing.cast(rich.progress.TaskID, task_id),
                    total=1,
                    completed=1,
                )
                animation.stop()

                if settings["json"]:
                    return console.print_json(data={"accepted": r_total})

                return console.print(f"Accepted {r_total} save instance(s).")

            case PrimitiveSignal.KILL:
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

    try:
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            tarfile.TarFile(name=path, stream=True) as tar,
        ):
            temp_dir = pathlib.Path(temp_dir)

            yield (ExtractSignal.EXTRACTING, 0)

            tar.extractall(temp_dir)

            with (temp_dir / "entities.json").open() as buffer:
                entities: collections.abc.Sequence[Save] = json.load(buffer)

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


@merger(action=action, presentation=presentation)
def save_extract_command(
    in_: collections.abc.Generator[tuple[ExtractSignal, float]],
    pole: collections.abc.Generator[
        None, tuple[ExtractSignal, float] | PrimitiveSignal
    ],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == ExtractSignal.FAILED:
            exit(1)

    pole.send(PrimitiveSignal.FINISHED)

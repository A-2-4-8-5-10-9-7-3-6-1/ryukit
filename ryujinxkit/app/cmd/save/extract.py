"""Extract command."""

import collections
import collections.abc
import enum
import json
import pathlib
import sqlite3
import tarfile
import tempfile
import typing

import rich
import rich.progress
import rich.status
import rich.table
import typer

from ....core.db.models.save import Save
from ....core.db.theme import db_applier
from ....core.fs.resolver import Node, resolver
from ....core.ui.objects import console
from ....core.ui.theme import ui_applier
from ....helpers.AP_decomp import Presenter, PrimitiveSignal, merge
from ...context.behavioural_control import settings
from .typer import save_typer


class ExtractSignal(int, enum.Enum):
    EXTRACTING = 0
    FAILED = 1
    READING = 2


@save_typer.command("extract")
def command(
    path: typing.Annotated[
        pathlib.Path,
        typer.Argument(
            metavar="PATH",
            exists=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to your extract.",
        ),
    ],
):
    """
    Extract saves from an export.
    """

    merge(_action_dispensor, _presenter())(path)


def _presenter() -> Presenter[tuple[ExtractSignal, float]]:
    reading_progress = False
    animation: rich.progress.Progress | rich.status.Status | None = None
    task_id: rich.progress.TaskID | None = None
    r_total: float | None = None

    while True:
        match (yield):
            case ExtractSignal.EXTRACTING, 0:
                animation = ui_applier(rich.status.Status)("Extracting...")

                animation.start()

            case ExtractSignal.FAILED, 0:
                reading_progress = False

                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    console.print_json(data={"code": "EXTRACTION_ISSUE"})

                    continue

                console.print("Malformed export file.", style="error")

            case ExtractSignal.READING, volume:
                if reading_progress:
                    typing.cast(rich.progress.Progress, animation).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                typing.cast(rich.status.Status, animation).stop()

                animation = ui_applier(rich.progress.Progress)(
                    ui_applier(rich.progress.SpinnerColumn)(),
                    "{task.description}",
                    "({task.percentage:.1f}%)",
                )
                task_id = animation.add_task(
                    description="Reading entities...", total=volume
                )
                r_total = volume
                reading_progress = True

                animation.start()

            case PrimitiveSignal.FINISHED:
                reading_progress = False
                r_total = typing.cast(int, r_total)
                animation = typing.cast(rich.progress.Progress, animation)

                animation.update(
                    task_id=typing.cast(rich.progress.TaskID, task_id),
                    total=1,
                    completed=1,
                )
                animation.stop()

                if settings["json"]:
                    console.print_json(data={"accepted": r_total})

                    continue

                console.print(f"Accepted {r_total} save instance(s).")

            case PrimitiveSignal.KILL:
                if animation is not None:
                    animation.stop()

            case _:
                pass


def _action_dispensor(path: pathlib.Path):
    """Extract saves from an export.

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

            with db_applier(sqlite3.connect)("DATABASE") as con:
                for entity in entities:
                    save_dir = (
                        temp_dir
                        / resolver[Node.RYUJINXKIT_SAVE_FOLDER].name
                        / str(entity["id"])
                    )

                    con.execute(
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
                            str(con.cursor().lastrowid),
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
        yield PrimitiveSignal.KILL

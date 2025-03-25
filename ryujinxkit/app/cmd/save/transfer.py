"""Operate command."""

import collections
import collections.abc
import enum
import pathlib
import shutil
import sqlite3
import typing

import rich
import rich.progress
import typer

from ....core.db.theme import db_applier
from ....core.fs.resolver import Node, resolver
from ....core.ui.objects import console
from ....core.ui.theme import ui_applier
from ....helpers.AP_decomp import Presenter, PrimitiveSignal, merge
from ...context.behavioural_control import settings
from .typer import save_typer


class TransferOperation(str, enum.Enum):
    RESTORE = "restore"
    UPDATE = "update"


class _TransferSignal(int, enum.Enum):
    FAILED = 0
    TRANSFERING = 1


@save_typer.command("operate", epilog="Aliases: op")
@save_typer.command("op", hidden=True)
def command(
    operation: typing.Annotated[
        TransferOperation, typer.Argument(help="Operation to perform.")
    ],
    id_: typing.Annotated[
        str,
        typer.Argument(metavar="ID", help="Save's ID.", case_sensitive=False),
    ],
):
    """
    Operate on save instances through file transference.
    """

    merge(_action_dispensor, _presenter())(id_=id_, operation=operation)


def _action_dispensor(id_: str, operation: TransferOperation):
    """Transfer state between a save instance and Ryujinx.

    :param id_: Save-state's ID as a string.
    :param operation: Usage operation.

    :returns: Signal generator for transfer commands.
    """

    Configs = typing.TypedDict(
        "Configs",
        {
            "order": collections.abc.Callable[
                [tuple[Node, ...]], tuple[pathlib.Path, ...]
            ],
            "size": collections.abc.Callable[
                [collections.abc.Iterable[pathlib.Path]], int
            ],
        },
    )

    with db_applier(sqlite3.connect)("DATABASE") as con:
        total = 0
        initial_size: int = -1

        try:
            initial_size = next(
                con.execute(
                    """
                    SELECT size
                    FROM saves
                    WHERE id = :id;
                    """,
                    {"id": id_},
                )
            )[0]

        except StopIteration:
            yield (_TransferSignal.FAILED, 0)
            yield PrimitiveSignal.KILL

        configs: Configs = (
            {
                "order": lambda pair: tuple(map(resolver.__getitem__, pair)),
                "size": lambda _: initial_size,
            }
            if operation == TransferOperation.RESTORE
            else {
                "order": lambda p: tuple(
                    map(resolver.__getitem__, reversed(p))
                ),
                "size": lambda members: sum(
                    path.stat().st_size for path in members
                ),
            }
        )

        yield (_TransferSignal.TRANSFERING, 3)

        with resolver.cache_locked(
            (Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
        ):
            for source, dest in map(
                configs["order"],
                [
                    (
                        Node.RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE,
                        Node.RYUJINX_SYSTEM_SAVE,
                    ),
                    (
                        Node.RYUJINXKIT_SAVE_INSTANCE_SAVE_META,
                        Node.RYUJINX_SAVE_META,
                    ),
                    (
                        Node.RYUJINXKIT_SAVE_INSTANCE_SAVE,
                        Node.RYUJINX_USER_SAVE,
                    ),
                ],
            ):
                members = [
                    path for path in source.rglob("*") if not path.is_dir()
                ]
                total += configs["size"](members)

                if dest.exists():
                    shutil.rmtree(dest)

                for path in members:
                    bucket = dest / path.relative_to(source)

                    bucket.parent.mkdir(parents=True, exist_ok=True)
                    bucket.write_bytes(path.read_bytes())

                yield (_TransferSignal.TRANSFERING, 1)

        if operation == TransferOperation.UPDATE:
            con.execute(
                """
                UPDATE saves
                SET size = :total
                WHERE id = :id;
                """,
                {"id": id_, "total": total},
            )


def _presenter() -> Presenter[tuple[_TransferSignal, float]]:
    looping = False
    animation: rich.progress.Progress | None = None
    task_id: rich.progress.TaskID | None = None

    while True:
        match (yield):
            case _TransferSignal.FAILED, 0:
                if settings["json"]:
                    console.print_json(data={"code": "ID_ISSUE"})

                    continue

                console.print("[error]Unrecognized save ID.")

            case _TransferSignal.TRANSFERING, volume:
                if looping:
                    typing.cast(rich.progress.Progress, animation).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                animation = ui_applier(rich.progress.Progress)(
                    ui_applier(rich.progress.SpinnerColumn)(),
                    "{task.description}",
                    "({task.completed}/{task.total})",
                )
                task_id = animation.add_task(
                    description="Transfering", total=volume
                )
                looping = True

                animation.start()

            case PrimitiveSignal.FINISHED:
                looping = False

                typing.cast(rich.progress.Progress, animation).stop()

                if settings["json"]:
                    continue

                console.print("Transfer successful.")

            case PrimitiveSignal.KILL:
                if animation is not None:
                    animation.stop()

            case _:
                pass

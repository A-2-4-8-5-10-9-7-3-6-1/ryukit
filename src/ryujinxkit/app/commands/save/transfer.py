"""Save-transfer command.

Exports
-------
- :class:`TransferOperation`: Options for the save-transfer command.
- :func:`save_transfer_command`: The save-transfer command.
"""

import collections
import collections.abc
import enum
import pathlib
import shutil
import typing

import rich
import rich.progress

from ....core.db.connection import connect
from ....core.fs.resolver import Node, resolver
from ....core.ui.configs import UI_CONFIGS
from ....core.ui.objects import console
from ...context import settings
from ..AP_decomp import PrimitiveSignal, merger


class TransferOperation(str, enum.Enum):
    RESTORE = "restore"
    UPDATE = "update"


class TransferSignal(int, enum.Enum):
    FAILED = 0
    TRANSFERING = 1


def action(
    id_: str, operation: TransferOperation
) -> collections.abc.Generator[tuple[TransferSignal, float]]:
    """
    Transfer state between a save instance and Ryujinx.

    :param id_: Save-state's ID as a string.
    :param operation: Usage operation.

    :returns: Signal generator for transfer commands.
    """

    Config = typing.TypedDict(
        "Config",
        {
            "query": str,
            "order": collections.abc.Callable[
                [tuple[Node, ...]], tuple[pathlib.Path, ...]
            ],
            "size": collections.abc.Callable[
                [collections.abc.Iterable[pathlib.Path]], int
            ],
        },
    )

    with connect() as connection:
        total = 0
        initial_size: int = -1

        try:
            initial_size = next(
                connection.execute(
                    f"""
                    SELECT size
                    FROM saves
                    WHERE id = :id;
                    """,
                    {"id": id_},
                )
            )[0]

        except StopIteration:
            yield (TransferSignal.FAILED, 0)

        config: Config = (
            {
                "query": """
                    UPDATE saves
                    SET used = datetime("now")
                    WHERE id = :id;
                    """,
                "order": lambda p: tuple(map(resolver.__getitem__, p)),
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
                "query": """
                    UPDATE saves
                    SET updated = datetime("now"), size = :total
                    WHERE id = :id;
                    """,
            }
        )

        yield (TransferSignal.TRANSFERING, 3)

        with resolver.cache_locked(
            (Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
        ):
            for source, dest in map(
                config["order"],
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
                total += config["size"](members)

                if dest.exists():
                    shutil.rmtree(dest)

                for path in members:
                    bucket = dest / path.relative_to(source)

                    bucket.parent.mkdir(parents=True, exist_ok=True)
                    bucket.write_bytes(path.read_bytes())

                yield (TransferSignal.TRANSFERING, 1)

        connection.execute(config["query"], {"id": id_, "total": total})


def presenter() -> (
    collections.abc.Generator[
        None, tuple[TransferSignal, float] | PrimitiveSignal
    ]
):
    looping = False
    animation: rich.progress.Progress | None = None
    task_id: rich.progress.TaskID | None = None

    while True:
        match (yield):
            case TransferSignal.FAILED, 0:
                if settings["json"]:
                    return console.print_json(data={"code": "ID_ISSUE"})

                return console.print("Unrecognized save ID.")

            case TransferSignal.TRANSFERING, volume:
                if looping:
                    typing.cast(rich.progress.Progress, animation).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                animation = rich.progress.Progress(
                    rich.progress.SpinnerColumn(style="dim"),
                    "[dim]{task.description}",
                    "[dim]({task.completed}/{task.total})",
                    console=console,
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
                    transient=True,
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
                    return

                return console.print("Transfer successful.")

            case PrimitiveSignal.KILL:
                if animation is not None:
                    animation.stop()

                return

            case _:
                pass


@merger(action=action, presenter=presenter)
def save_transfer_command(
    in_: collections.abc.Generator[tuple[TransferSignal, float]],
    pole: collections.abc.Generator[
        None, tuple[TransferSignal, float] | PrimitiveSignal
    ],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == TransferSignal.FAILED:
            exit(1)

    pole.send(PrimitiveSignal.FINISHED)

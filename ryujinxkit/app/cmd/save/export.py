"""Export command."""

import io
import json
import pathlib
import sqlite3
import tarfile
import typing

import rich
import rich.status
import typer

from ....core.db.theme_applier import db_ready
from ....core.fs.resolver import Node, resolver
from ....core.ui.objects import console
from ....core.ui.theme_applier import styled
from ....helpers.AP_decomp import Presenter, PrimitiveSignal, merge
from .typer import save_typer


@save_typer.command("export")
def command(
    output: typing.Annotated[
        pathlib.Path, typer.Option(help="Output-file's path.")
    ] = pathlib.Path("ryujinxkit-saves.tar"),
):
    """
    Export your saves to a tar file.
    """

    merge(_action_dispensor, _presenter())(output)


def _presenter() -> Presenter[None]:
    status = styled(rich.status.Status)("Exporting...")
    accepting = True

    while True:
        match (yield):
            case _ if not accepting:
                pass

            case PrimitiveSignal.FINISHED:
                status.stop()
                console.print("Export completed.")

            case _:
                status.start()


def _action_dispensor(output: pathlib.Path):
    """Archive saves into a tar file.

    :param output: Output's file path.
    """

    with (
        tarfile.TarFile(name=output, mode="w") as tar,
        db_ready(sqlite3.connect)("DATABASE") as con,
    ):
        entities = tarfile.TarInfo("entities.json")

        with io.BytesIO() as buffer:
            entities.size = buffer.write(
                json.dumps(
                    list(
                        map(
                            dict,
                            con.execute(
                                """
                                SELECT id, tag, created, updated, used, size
                                FROM saves;
                                """
                            ),
                        )
                    )
                ).encode()
            )

            buffer.seek(0)
            tar.addfile(tarinfo=entities, fileobj=buffer)

        for id_ in map(
            lambda x: str(x["id"]),
            con.execute(
                """
                SELECT id
                FROM saves;
                """
            ),
        ):
            with resolver.cache_locked(
                (Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
            ):
                if not resolver[Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER].exists():
                    continue

                [
                    tar.add(
                        name=path,
                        arcname=path.relative_to(
                            resolver[Node.RYUJINXKIT_ROAMING_DATA]
                        ),
                    )
                    for path in resolver[
                        Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                    ].rglob("*")
                    if not path.is_dir()
                ]

    yield

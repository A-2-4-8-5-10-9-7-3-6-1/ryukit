"""Save-export command.

Exports
-------
- :func:`save_export_command`: The save-export command.
"""

import collections
import collections.abc
import io
import json
import pathlib
import tarfile

import rich
import rich.status

from ....core.db.connection import connect
from ....core.fs.resolver import Node, resolver
from ....core.ui.objects import console
from ....core.ui.styling import styled
from ..AP_decomp import PrimitiveSignal, merger


def presentation() -> collections.abc.Generator[None, None | PrimitiveSignal]:
    with styled(rich.status.Status)(status="Exporting..."):
        signal = yield

    if signal != PrimitiveSignal.FINISHED:
        return

    console.print("Export completed.")


def action(output: pathlib.Path) -> None:
    """Archive saves into a tar file.

    :param output: Output's file path.
    """

    with (
        tarfile.TarFile(name=output, mode="w") as tar,
        connect() as connection,
    ):
        entities = tarfile.TarInfo("entities.json")

        with io.BytesIO() as buffer:
            entities.size = buffer.write(
                json.dumps(
                    list(
                        map(
                            dict,
                            connection.execute(
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
            connection.execute(
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


@merger(action=action, presentation=presentation)
def save_export_command(
    in_: None, pole: collections.abc.Generator[None, None | PrimitiveSignal]
) -> None:
    next(pole)

import io
import json
import pathlib
import tarfile

from ryujinxkit.file_access.resolver import resolver

from ....database.connection import connect
from ....file_access.resolver_node import ResolverNode


def action(output: pathlib.Path) -> None:
    """
    Archive saves into a tar file.

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
                    [
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
                        for record in connection.execute(
                            """
                            SELECT id, tag, created, updated, used, size
                            FROM saves;
                            """
                        )
                    ]
                ).encode()
            )

            buffer.seek(0)

            tar.addfile(tarinfo=entities, fileobj=buffer)

        for (id_,) in connection.execute(
            """
            SELECT CAST(id AS TEXT)
            FROM saves;
            """
        ):
            with resolver.cache_locked(
                (ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
            ):
                if not resolver[
                    ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                ].exists():
                    continue

                [
                    tar.add(
                        name=path,
                        arcname=path.relative_to(
                            resolver[ResolverNode.RYUJINXKIT_ROAMING_DATA]
                        ),
                    )
                    for path in resolver[
                        ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                    ].rglob("*")
                    if not path.is_dir()
                ]

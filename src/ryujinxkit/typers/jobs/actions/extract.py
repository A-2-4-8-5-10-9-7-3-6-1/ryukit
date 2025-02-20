import collections.abc
import datetime
import json
import pathlib
import tarfile
import tempfile
import typing

from ryujinxkit.file_access.resolver import resolver

from ....database.connection import connect
from ....file_access.resolver_node import ResolverNode
from ..messages.extract import ExtractSignal


class _Entity(typing.TypedDict):
    tag: str
    created: datetime.date
    updated: datetime.date
    used: datetime.date
    size: int
    id: int


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
            entities: collections.abc.Sequence[_Entity]

            yield (ExtractSignal.EXTRACTING, 0)

            tar.extractall(temp_dir)

            with (temp_dir / "entities.json").open() as buffer:
                entities = json.load(buffer)

            yield (ExtractSignal.READING, len(entities))

            with connect() as connection:
                for entity in entities:
                    save_dir = (
                        temp_dir
                        / resolver[ResolverNode.RYUJINXKIT_SAVE_FOLDER].name
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
                            ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                            str(connection.cursor().lastrowid),
                        )
                    ):
                        for entry in save_dir.rglob("*"):
                            subpath = resolver[
                                ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
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

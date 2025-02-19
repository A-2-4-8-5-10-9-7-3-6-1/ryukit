import collections.abc
import json
import pathlib
import tarfile
import tempfile
import typing

from ryujinxkit.file_access.resolver import resolver

from ....database.connection import connect
from ....file_access.resolver_node import ResolverNode
from ..messages.extract import ExtractSignal


def action(
    path: pathlib.Path,
) -> collections.abc.Generator[tuple[ExtractSignal, float]]:
    """
    Extract saves from an export.

    :param path: Path to your export.
    """

    try:
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            tarfile.TarFile(name=path, stream=True) as tar,
        ):
            temp_dir = pathlib.Path(temp_dir)
            states: collections.abc.Sequence[dict[str, typing.Any]]

            yield (ExtractSignal.EXTRACTING, 0)

            tar.extractall(path=temp_dir)

            with (temp_dir / "entities.json").open() as buffer:
                states = json.load(fp=buffer)

            yield (ExtractSignal.READING, len(states))

            with connect() as connection:
                for state in states:
                    save_dir = (
                        temp_dir
                        / resolver[ResolverNode.RYUJINXKIT_SAVE_FOLDER].name
                        / str(state["id"])
                    )

                    connection.execute(
                        """
                        INSERT INTO saves (tag, created, updated, used, size)
                        VALUES (:tag, :created, :updated, :used, :size);
                        """,
                        state,
                    )

                    if state["size"] == 0:
                        yield (ExtractSignal.READING, 1)

                        continue

                    with resolver.cache_locked(
                        (
                            ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER,
                            str(connection.cursor().lastrowid),
                        )
                    ):
                        for entry in save_dir.rglob(pattern="*"):
                            subpath = resolver[
                                ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER
                            ] / entry.relative_to(save_dir)

                            if entry.is_dir():
                                subpath.mkdir(parents=True, exist_ok=True)

                                continue

                            subpath.write_bytes(data=entry.read_bytes())

                            yield (
                                ExtractSignal.READING,
                                subpath.stat().st_size / state["size"],
                            )

    except Exception:
        yield (ExtractSignal.FAILED, 0)

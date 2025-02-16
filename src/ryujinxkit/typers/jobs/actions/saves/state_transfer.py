"""
- dependency level 3.
"""

import collections.abc
import pathlib
import shutil
import typing

from .....database.connection import connect
from .....file_access.resolver import resolver
from .....file_access.resolver_node import ResolverNode


def action(
    id_: str,
    operation: typing.Literal["restore", "update"],
) -> collections.abc.Generator[tuple[str, float]]:
    """
    Transfer state between a save instance and Ryujinx.

    :param %id_%: Save-state's ID as a string.
    :param operation: Usage operation.
    """

    with connect() as connection:
        total: int = 0
        initial_size: int = -1

        try:
            initial_size = next(
                connection.execute(
                    """
                    SELECT size
                    FROM saves
                    WHERE id = ?;
                    """,
                    [id_],
                )
            )[0]

        except StopIteration:
            yield ("TRANSFERING", -1)

        query: collections.abc.Callable[[int], tuple[str, list[typing.Any]]]
        order: collections.abc.Callable[
            [ResolverNode, ResolverNode],
            tuple[ResolverNode, ResolverNode],
        ]
        size: collections.abc.Callable[
            [collections.abc.Iterable[pathlib.Path]],
            int,
        ]

        match operation:
            case "restore":
                order = lambda x, y: (x, y)
                size = lambda _: initial_size
                query = lambda _: (
                    """
                    UPDATE saves
                    SET used = datetime("now")
                    WHERE id = ?;
                    """,
                    [id_],
                )

            case "update":
                order = lambda x, y: (y, x)
                size = lambda members: sum(
                    path.stat().st_size for path in members
                )
                query = lambda total: (
                    """
                    UPDATE saves
                    SET updated = datetime("now"), size = ?
                    WHERE id = ?;
                    """,
                    [total, id_],
                )

        yield ("TRANSFERING", 3)

        with resolver.cache_locked(
            (ResolverNode.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
        ):
            for source, dest in [
                map(
                    resolver.__getitem__,
                    order(
                        ResolverNode.RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE,
                        ResolverNode.RYUJINX_SYSTEM_SAVE,
                    ),
                ),
                map(
                    resolver.__getitem__,
                    order(
                        ResolverNode.RYUJINXKIT_SAVE_INSTANCE_SAVE_META,
                        ResolverNode.RYUJINX_SAVE_META,
                    ),
                ),
                map(
                    resolver.__getitem__,
                    order(
                        ResolverNode.RYUJINXKIT_SAVE_INSTANCE_SAVE,
                        ResolverNode.RYUJINX_USER_SAVE,
                    ),
                ),
            ]:
                members = [
                    path
                    for path in source.rglob(pattern="*")
                    if not path.is_dir()
                ]
                total += size(members)

                if dest.exists():
                    shutil.rmtree(path=dest)

                for path in members:
                    bucket = dest / path.relative_to(source)

                    bucket.parent.mkdir(parents=True, exist_ok=True)
                    bucket.write_bytes(data=path.read_bytes())

                yield ("TRANSFERING", 1)

        connection.execute(*query(total))

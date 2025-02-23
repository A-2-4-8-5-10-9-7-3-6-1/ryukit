import collections.abc
import pathlib
import shutil
import typing

from .....core.fs.node import Node
from .....core.fs.resolver import resolver
from .....services.sqlite3.connection import connect
from .signals import StateTransferSignal
from .transfer_op import TransferOp


def action(
    id_: str,
    operation: TransferOp,
) -> collections.abc.Generator[tuple[StateTransferSignal, float]]:
    """
    Transfer state between a save instance and Ryujinx.

    :param %id_%: Save-state's ID as a string.
    :param operation: Usage operation.

    :returns: Signal generator for transfer commands.
    """

    with connect() as connection:
        total = 0
        initial_size = -1

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
            yield (StateTransferSignal.FAILED, 0)

        query: collections.abc.Callable[[int], tuple[str, list[typing.Any]]]
        order: collections.abc.Callable[
            [Node, Node],
            tuple[Node, Node],
        ]
        size: collections.abc.Callable[
            [collections.abc.Iterable[pathlib.Path]],
            int,
        ]

        match operation:
            case TransferOp.RESTORE:
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

            case TransferOp.UPDATE:
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

        yield (StateTransferSignal.TRANSFERING, 3)

        with resolver.cache_locked(
            (Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)
        ):
            for source, dest in [
                map(
                    resolver.__getitem__,
                    order(
                        Node.RYUJINXKIT_SAVE_INSTANCE_SYSTEM_SAVE,
                        Node.RYUJINX_SYSTEM_SAVE,
                    ),
                ),
                map(
                    resolver.__getitem__,
                    order(
                        Node.RYUJINXKIT_SAVE_INSTANCE_SAVE_META,
                        Node.RYUJINX_SAVE_META,
                    ),
                ),
                map(
                    resolver.__getitem__,
                    order(
                        Node.RYUJINXKIT_SAVE_INSTANCE_SAVE,
                        Node.RYUJINX_USER_SAVE,
                    ),
                ),
            ]:
                members = [
                    path for path in source.rglob("*") if not path.is_dir()
                ]
                total += size(members)

                if dest.exists():
                    shutil.rmtree(dest)

                for path in members:
                    bucket = dest / path.relative_to(source)

                    bucket.parent.mkdir(parents=True, exist_ok=True)
                    bucket.write_bytes(path.read_bytes())

                yield (StateTransferSignal.TRANSFERING, 1)

        connection.execute(*query(total))

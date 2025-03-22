"""Save-delete command.

Exports
-------
- :func:`save_delete_command`: The save-delete command.
"""

import collections
import collections.abc
import shutil

from ....core.db.connection import connect
from ....core.fs.resolver import Node, resolver
from ....core.ui.objects import console
from ...context import settings
from ..AP_decomp import PrimitiveSignal, merger


def presentation() -> collections.abc.Generator[None, bool | PrimitiveSignal]:
    signal = yield

    if isinstance(signal, PrimitiveSignal) or settings["json"]:
        return

    if signal:
        return console.print("Save deleted.")

    console.print("[error]Unrecognized save ID.")


def action(id_: str) -> bool:
    """Delete a save.

    :param id_: Save's ID.

    :returns: Whether or not the operation was successful.
    """

    with connect() as connection:
        if (
            connection.execute(
                """
                DELETE FROM saves
                WHERE id = :id;
                """,
                {"id": id_},
            ).rowcount
            == 0
        ):
            return False

    with resolver.cache_locked((Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)):
        if resolver[Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER].exists():
            shutil.rmtree(resolver[Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER])

    return True


@merger(action=action, presentation=presentation)
def save_delete_command(
    in_: bool, pole: collections.abc.Generator[None, bool | PrimitiveSignal]
) -> None:
    pole.send(in_)

    if not in_:
        exit(1)

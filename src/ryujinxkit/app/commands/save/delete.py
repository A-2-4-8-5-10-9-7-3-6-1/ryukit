import collections
import collections.abc
import shutil

from ....core.fs.node import Node
from ....core.fs.resolver import resolver
from ....core.ui.console import console
from ....services.sqlite3.connection import connect
from ...context import settings
from ..merger import merger
from ..signals import Primer

__all__ = ["delete_command"]


def presenter() -> collections.abc.Generator[None, bool | Primer]:
    signal = yield

    if isinstance(signal, Primer):
        return

    if settings["json"]:
        return console.print_json(data={"success": signal})

    if signal:
        return console.print("Save deleted.")

    console.print("Unrecognized save ID.")


def action(id_: str) -> bool:
    """
    Delete a save.

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


@merger(action=action, presenter=presenter)
def delete_command(
    in_: bool, pole: collections.abc.Generator[None, bool | Primer]
) -> None:
    pole.send(in_)

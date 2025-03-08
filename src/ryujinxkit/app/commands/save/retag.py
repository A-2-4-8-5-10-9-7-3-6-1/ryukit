import collections
import collections.abc

from ....core.db.connection import connect
from ....core.ui.objects import console
from ...context import settings
from ..merger import merger
from ..signals import Primer

__all__ = ["retag_command"]


def presenter() -> collections.abc.Generator[None, bool | Primer]:
    signal = yield

    if isinstance(signal, Primer) or settings["json"]:
        return

    if signal:
        return console.print("Tag updated.")

    console.print("Unrecognized save ID.")


def action(id_: str, tag: str) -> bool:
    """
    Change a save's tagging.

    :param id_: The save's ID.
    :param tag: The save's new tag.

    :returns: Whether or not the operation was successful.
    """

    with connect() as connection:
        return (
            connection.execute(
                """
                UPDATE saves
                SET tag = :tag, updated = datetime("now")
                WHERE id = :id;
                """,
                {"tag": tag, "id": id_},
            ).rowcount
            != 0
        )


@merger(action=action, presenter=presenter)
def retag_command(
    in_: bool, pole: collections.abc.Generator[None, bool | Primer]
) -> None:
    pole.send(in_)

    if not in_:
        exit(1)

"""Save-retag command.

Exports
-------
- :func:`save_retag_command`: The save-retag command.
"""

import collections
import collections.abc

from ....core.db.connection import connect
from ....core.ui.objects import console
from ...context import settings
from ..AP_decomp import PrimitiveSignal, merger


def presenter() -> collections.abc.Generator[None, bool | PrimitiveSignal]:
    signal = yield

    if isinstance(signal, PrimitiveSignal) or settings["json"]:
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
def save_retag_command(
    in_: bool, pole: collections.abc.Generator[None, bool | PrimitiveSignal]
) -> None:
    pole.send(in_)

    if not in_:
        exit(1)

"""Save-create command.

Exports
-------
- :func:`save_create_command`: The save-create command.
"""

import collections
import collections.abc
import typing

from ....core.db.configs import DB_CONFIGS
from ....core.db.connection import connect
from ....core.ui.objects import console
from ...context import settings
from ..AP_decomp import PrimitiveSignal, merger


def action(tag: str = DB_CONFIGS["defaults"]["save_tag"]) -> int:
    """Create a save.

    :param tag: A tag for the save.

    :returns: ID of new save.
    """

    with connect() as connection:
        return typing.cast(
            int,
            connection.execute(
                """
                INSERT INTO saves (tag)
                VALUES (:tag);
                """,
                {"tag": tag},
            ).lastrowid,
        )


def presentation() -> collections.abc.Generator[None, int | PrimitiveSignal]:
    signal = yield

    if isinstance(signal, PrimitiveSignal):
        return

    if settings["json"]:
        return console.print_json(data={"id": signal})

    console.print(f"ID: {signal}.")


@merger(action=action, presentation=presentation)
def save_create_command(
    in_: int, pole: collections.abc.Generator[None, int | PrimitiveSignal]
) -> None:
    pole.send(in_)

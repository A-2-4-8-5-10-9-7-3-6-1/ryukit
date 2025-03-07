import collections
import collections.abc
import typing

from ....core.ui.console import console
from ....services.sqlite3.configs import DB_CONFIGS
from ....services.sqlite3.connection import connect
from ...context import settings
from ..merger import merger
from ..signals import Primer

__all__ = ["create_command"]


def action(tag: str = DB_CONFIGS["defaults"]["save_tag"]) -> int:
    """
    Create a save.

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


def presenter() -> collections.abc.Generator[None, int | Primer]:
    signal = yield

    if isinstance(signal, Primer):
        return

    if settings["json"]:
        return console.print_json(data={"id": signal})

    console.print(f"ID: {signal}.")


@merger(action=action, presenter=presenter)
def create_command(
    in_: int, pole: collections.abc.Generator[None, int | Primer]
) -> None:
    pole.send(in_)

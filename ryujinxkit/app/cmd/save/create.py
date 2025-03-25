"""Create command."""

import sqlite3
import typing

import typer

from ....core.db.configs import DB_CONFIGS
from ....core.db.theme import db_applier
from ....core.ui.objects import console
from ....helpers.AP_decomp import Presenter, PrimitiveSignal, merge
from ....helpers.parsers import tag_parser
from ...context.behavioural_control import settings
from .typer import save_typer


@save_typer.command("create")
def command(
    tag: typing.Annotated[
        str,
        typer.Option(
            metavar="TAG", help="A tag for your save.", parser=tag_parser
        ),
    ] = DB_CONFIGS["defaults"]["save_tag"],
):
    """
    Create an empty save.
    """

    merge(_action_dispensor, _presenter())(tag)


def _action_dispensor(tag: str):
    """Create a save.

    :param tag: A tag for the save.

    :returns: ID of new save.
    """

    with db_applier(sqlite3.connect)("DATABASE") as con:
        yield typing.cast(
            int,
            con.execute(
                """
                INSERT INTO saves (tag)
                VALUES (:tag);
                """,
                {"tag": tag},
            ).lastrowid,
        )


def _presenter() -> Presenter[int]:
    while True:
        match (yield):
            case id_ if not isinstance(id_, PrimitiveSignal):
                if settings["json"]:
                    yield console.print_json(data={"id": id_})

                    continue

                console.print(f"ID: {id_}.")

            case _:
                pass

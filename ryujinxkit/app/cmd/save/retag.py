"""Retag command."""

import sqlite3
import typing

import typer

from ....core.db.theme import db_applier
from ....core.ui.objects import console
from ....helpers.AP_decomp import Presenter, PrimitiveSignal, merge
from ....helpers.parsers import tag_parser
from ...context.behavioural_control import settings
from .typer import save_typer


@save_typer.command("retag", epilog="Aliases: rt")
@save_typer.command("rt", hidden=True)
def command(
    id_: typing.Annotated[
        str, typer.Argument(metavar="ID", help="Save's ID.")
    ],
    tag: typing.Annotated[
        str,
        typer.Argument(
            metavar="TAG", help="Save's new tag.", parser=tag_parser
        ),
    ],
):
    """
    Change a save's tag.
    """

    merge(_action_dispensor, _presenter())(id_, tag)


def _presenter() -> Presenter[bool]:
    while True:
        match (yield):
            case signal if (
                isinstance(signal, PrimitiveSignal) or settings["json"]
            ):
                pass

            case status:
                if status:
                    console.print("Tag updated.")

                    continue

                console.print("[error]Unrecognized save ID.")


def _action_dispensor(id_: str, tag: str):
    """Change a save's tagging.

    :param id_: The save's ID.
    :param tag: The save's new tag.

    :returns: Whether or not the operation was successful.
    """

    with db_applier(sqlite3.connect)("DATABASE") as con:
        yield (
            con.execute(
                """
                UPDATE saves
                SET tag = :tag, updated = datetime("now")
                WHERE id = :id;
                """,
                {"tag": tag, "id": id_},
            ).rowcount
            != 0
        )

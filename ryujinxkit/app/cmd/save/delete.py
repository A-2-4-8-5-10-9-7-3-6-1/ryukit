"""Delete command."""

import shutil
import sqlite3
import typing

import typer

from ....core.db.theme import db_applier
from ....core.fs.resolver import Node, resolver
from ....core.ui.objects import console
from ....helpers.AP_decomp import Presenter, PrimitiveSignal, merge
from ...context.behavioural_control import settings
from .typer import save_typer


@save_typer.command("remove", epilog="Aliases: rm")
@save_typer.command("rm", hidden=True)
def command(
    id_: typing.Annotated[
        str, typer.Argument(metavar="ID", help="The save's ID.")
    ],
):
    """
    Remove a save.
    """

    merge(_action_dispensor, _presenter())(id_)


def _presenter() -> Presenter[bool]:
    while True:
        match (yield):
            case signal if (
                isinstance(signal, PrimitiveSignal) or settings["json"]
            ):
                pass

            case status:
                if status:
                    console.print("Save deleted.")

                    continue

                console.print("[error]Unrecognized save ID.")


def _action_dispensor(id_: str):
    """Delete a save.

    :param id_: Save's ID.

    :returns: Whether or not the operation was successful.
    """

    with db_applier(sqlite3.connect)("DATABASE") as con:
        if (
            con.execute(
                """
                DELETE FROM saves
                WHERE id = :id;
                """,
                {"id": id_},
            ).rowcount
            == 0
        ):
            yield False
            yield PrimitiveSignal.KILL

    with resolver.cache_locked((Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER, id_)):
        if resolver[Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER].exists():
            shutil.rmtree(resolver[Node.RYUJINXKIT_SAVE_INSTANCE_FOLDER])

    yield True

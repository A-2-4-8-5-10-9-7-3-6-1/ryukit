import collections.abc
import sqlite3
import typing

import rich.box
import rich.progress
import rich.table

from ryujinxkit.typers.context.settings import settings

from ....display.configs import UI_REFRESH_RATE
from ....display.console import console
from .enums.commands import Enum as Command
from .typing.presenter import Presenter


def present() -> Presenter[sqlite3.Cursor]:
    """
    Present information for the list command.
    """

    cursor: sqlite3.Cursor | Command

    with console.status(
        status="[dim]Collecting saves",
        spinner_style="dim",
        refresh_per_second=UI_REFRESH_RATE,
    ):
        cursor = yield

    if isinstance(cursor, Command):
        return

    if settings["json"]:
        return console.print_json(
            data={
                "size": len(cursor.fetchall()),
            }
        )

    quick_draw: bool = True
    no8: collections.abc.Iterable[typing.Any] = []
    table: rich.table.Table

    while not quick_draw or no8 == []:
        table = rich.table.Table(
            "ID",
            "TAG",
            "CREATED",
            "UPDATED",
            "USED",
            "SIZE",
            box=rich.box.Box(
                box="\n".join(
                    [
                        "    ",
                        "    ",
                        " -  ",
                        "    ",
                        "    ",
                        "    ",
                        "    ",
                        "    ",
                    ]
                ),
                ascii=True,
            ),
        )

        if no8 != []:
            table.add_row(*no8)

        try:
            [
                table.add_row(*next(cursor))
                for _ in range(7 if quick_draw else 6)
            ]

            no8 = next(cursor)
            quick_draw = False

        except StopIteration:
            quick_draw = True

        finally:
            if table.row_count != 0:
                console.print(table)

                if not quick_draw:
                    console.input()

            if quick_draw and no8 == []:
                break

    if table.row_count == 0:  # type: ignore
        return console.print("No save to show.")

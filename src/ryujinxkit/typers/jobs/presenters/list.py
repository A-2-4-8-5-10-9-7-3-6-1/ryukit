import collections.abc
import sqlite3
import typing

import rich.box
import rich.progress
import rich.style
import rich.table

from ....display.configs import UI_REFRESH_RATE
from ....display.console import console
from ...context.settings import settings
from ..messages.primers import Primer
from .types.presenter import Presenter


class TableVar(typing.TypedDict):
    inner: list[list[typing.Any]] | rich.table.Table
    add: collections.abc.Callable[[collections.abc.Iterable[typing.Any]], None]
    reset: collections.abc.Callable[[], None]
    count: collections.abc.Callable[[], int]
    breathe: collections.abc.Callable[[], None]


def present() -> Presenter[sqlite3.Cursor]:
    cursor: sqlite3.Cursor | Primer

    with console.status(
        status="[dim]Collecting saves",
        spinner_style="dim",
        refresh_per_second=UI_REFRESH_RATE,
    ):
        cursor = yield

    if isinstance(cursor, Primer):
        return

    quick_draw = True
    no8: collections.abc.Iterable[typing.Any] = []
    table: TableVar | None = None
    add: collections.abc.Callable[[collections.abc.Iterable[typing.Any]], None]
    buffer: dict[str, typing.Any] = {
        "inner": ([] if settings["json"] else None)
    }

    if isinstance(buffer["inner"], list):
        inner = typing.cast(list[list[typing.Any]], buffer["inner"])
        add = lambda x: inner[-1].append(x)
        buffer["reset"] = lambda: inner.append([])
        buffer["breathe"] = lambda: None
        buffer["count"] = lambda: len(inner)

    else:
        add = lambda x: typing.cast(rich.table.Table, buffer["inner"]).add_row(
            *x
        )
        buffer["reset"] = lambda: buffer.update(
            [
                (
                    "inner",
                    rich.table.Table(
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
                    ),
                )
            ]
        )
        buffer["breathe"] = lambda: (
            (
                console.print(buffer["inner"]),
                console.input() if not quick_draw else None,
            )
            if typing.cast(TableVar, buffer)["count"]() != 0
            else None
        )
        buffer["count"] = lambda: typing.cast(
            rich.table.Table,
            buffer["inner"],
        ).row_count

    buffer["add"] = add
    table = typing.cast(TableVar, buffer)

    while not quick_draw or no8 == []:
        table["reset"]()

        if no8 != []:
            table["add"](no8)

        try:
            [table["add"](next(cursor)) for _ in range(7 if quick_draw else 6)]

            no8 = next(cursor)
            quick_draw = False

        except StopIteration:
            quick_draw = True

        finally:
            table["breathe"]()

            if quick_draw and no8 == []:
                break

    if settings["json"]:
        return console.print_json(
            data={
                "batches": table["inner"],
            }
        )

    if table["count"]() == 0:
        return console.print("No save to show.")

"""Save-list command.

Exports
-------
- :func:`save_list_command`: The save-list command.
"""

import collections
import collections.abc
import typing

import rich
import rich.box
import rich.progress
import rich.style
import rich.table

from ....core.db.connection import connect
from ....core.db.models.save import Save
from ....core.ui.configs import UI_CONFIGS
from ....core.ui.objects import console
from ...context import settings
from ..AP_decomp import PrimitiveSignal, merger


class SaveRender(typing.TypedDict):
    id: str
    tag: str
    created: str
    updated: str
    used: str | None
    size: str


def action(
    order: collections.abc.Sequence[tuple[str, str]] | None = None,
) -> collections.abc.Generator[collections.abc.Generator[SaveRender]]:
    """
    List saves.

    :param order: The order in which to sort rows.

    :returns: Signal generator for list command.
    """

    with connect() as connection:
        yield (
            {
                "id": str(data["id"]),
                "tag": data["tag"],
                "created": data["created"].strftime("%d/%Y/%m %H:%M"),
                "updated": data["updated"].strftime("%d/%Y/%m %H:%M"),
                "used": data["used"]
                and data["used"].strftime("%d/%Y/%m %H:%M"),
                "size": f"{round(data["size"] / pow(2, 20), 2)}MB",
            }
            for data in map(
                lambda x: typing.cast(Save, x),
                connection.execute(
                    f"""
                    SELECT *
                    FROM saves {
                        f"\nORDER BY {
                            ", ".join(
                                f"{col} {direction.upper()}"
                                for col, direction in order
                            )
                        }"
                        if order
                        else ""
                    };
                    """
                ),
            )
        )


def presenter() -> (
    collections.abc.Generator[
        None, collections.abc.Generator[SaveRender] | PrimitiveSignal
    ]
):
    class TableVar(typing.TypedDict):
        inner: list[list[SaveRender]] | rich.table.Table
        add: collections.abc.Callable[[SaveRender], None]
        reset: collections.abc.Callable[[], None]
        count: collections.abc.Callable[[], int]
        breathe: collections.abc.Callable[[], None]

    with console.status(
        status="[dim]Collecting saves",
        spinner_style="dim",
        refresh_per_second=UI_CONFIGS["refresh_rate"],
    ):
        reel = yield

    if isinstance(reel, PrimitiveSignal):
        return

    quick_draw = True
    no8: SaveRender | None = None
    table: TableVar | None = None
    add: collections.abc.Callable[[SaveRender], None]
    buffer: dict[str, typing.Any] = {
        "inner": ([] if settings["json"] else None)
    }

    if isinstance(buffer["inner"], list):
        inner = typing.cast(list[list[SaveRender]], buffer["inner"])
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
            rich.table.Table, buffer["inner"]
        ).row_count

    buffer["add"] = add
    table = typing.cast(TableVar, buffer)

    while not quick_draw or not no8:
        table["reset"]()

        if no8:
            table["add"](no8)

        try:
            [table["add"](next(reel)) for _ in range(7 if quick_draw else 6)]

            no8 = next(reel)
            quick_draw = False

        except StopIteration:
            quick_draw = True

        finally:
            table["breathe"]()

            if quick_draw and not no8:
                break

    if settings["json"]:
        return console.print_json(data={"batches": table["inner"]})

    if table["count"]() == 0:
        return console.print("No save to show.")


@merger(action=action, presenter=presenter)
def save_list_command(
    in_: collections.abc.Generator[collections.abc.Generator[SaveRender]],
    pole: collections.abc.Generator[
        None, collections.abc.Generator[SaveRender] | PrimitiveSignal
    ],
) -> None:
    pole.send(next(in_))

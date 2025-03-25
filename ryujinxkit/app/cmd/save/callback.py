"""Callback for the save typer."""

import collections
import collections.abc
import datetime
import sqlite3
import typing

import rich
import rich.box
import rich.progress
import rich.status
import rich.style
import rich.table
import typer

from ....core.db.models.save import Save
from ....core.db.theme_applier import db_ready
from ....core.ui.objects import console
from ....core.ui.theme_applier import styled
from ....helpers.AP_decomp import Presenter, PrimitiveSignal, merge
from ....helpers.parsers import sort_key_parser
from ...context.behavioural_control import settings
from .typer import save_typer


class _SaveRender(typing.TypedDict):
    id: str
    tag: str
    created: str
    updated: str
    used: str | None
    size: str


@save_typer.callback()
def callback(
    ctx: typer.Context,
    keys: typing.Annotated[
        list[object],
        typer.Option(
            "-k",
            "--key",
            metavar="SORT_KEY",
            parser=sort_key_parser,
            help="A sort key.",
        ),
    ] = ["used-", "updated-", "created-", "tag-", "size-"],
):
    """
    Execute save-related tasks, displaying save instances on a no-arg
    invocation.
    """

    if ctx.invoked_subcommand is None:
        merge(_action_dispensor, _presenter())(
            typing.cast(list[tuple[str, str]], keys)
        )


def _action_dispensor(
    order: collections.abc.Sequence[tuple[str, str]] | None = None,
):
    """List saves.

    :param order: The order in which to sort rows.

    :returns: Signal generator for list command.
    """

    with db_ready(sqlite3.connect)("DATABASE") as con:
        yield (
            typing.cast(
                _SaveRender,
                {
                    "id": str(data["id"]),
                    "tag": data["tag"],
                    "created": datetime.datetime.strptime(
                        data["created"], "%Y-%m-%d %H:%M:%S"
                    ).strftime("%d/%Y/%m %H:%M"),
                    "updated": datetime.datetime.strptime(
                        data["updated"], "%Y-%m-%d %H:%M:%S"
                    ).strftime("%d/%Y/%m %H:%M"),
                    "used": data["used"]
                    and datetime.datetime.strptime(
                        data["used"], "%Y-%m-%d %H:%M:%S"
                    ).strftime("%d/%Y/%m %H:%M"),
                    "size": f"{round(data["size"] / pow(2, 20), 2)}MB",
                },
            )
            for data in map(
                lambda x: typing.cast(Save, x),
                con.execute(
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


def _presenter() -> Presenter[collections.abc.Generator[_SaveRender]]:
    TableVar = typing.TypedDict(
        "TableVar",
        {
            "inner": list[list[_SaveRender]] | rich.table.Table,
            "add": collections.abc.Callable[[_SaveRender], None],
            "reset": collections.abc.Callable[[], None],
            "count": collections.abc.Callable[[], int],
            "breathe": collections.abc.Callable[[], None],
        },
    )
    status = styled(rich.status.Status)("Collecting saves...")
    quick_draw = True
    no8: _SaveRender | None = None
    table: TableVar | None = None
    add: collections.abc.Callable[[_SaveRender], None]
    buffer: dict[str, object] = {"inner": ([] if settings["json"] else None)}

    while True:
        match (yield):
            case PrimitiveSignal.START:
                status.start()

            case signal if isinstance(signal, PrimitiveSignal):
                status.stop()

            case reel:
                reel = typing.cast(
                    collections.abc.Generator[_SaveRender], reel
                )

                if isinstance(buffer["inner"], list):
                    inner = typing.cast(
                        list[list[_SaveRender]], buffer["inner"]
                    )
                    add = lambda x: inner[-1].append(x)
                    buffer["reset"] = lambda: inner.append([])
                    buffer["breathe"] = lambda: None
                    buffer["count"] = lambda: len(inner)

                else:
                    add = lambda x: typing.cast(
                        rich.table.Table, buffer["inner"]
                    ).add_row(
                        x["id"],
                        x["tag"],
                        x["created"],
                        x["updated"],
                        x["used"],
                        x["size"],
                    )
                    buffer["reset"] = lambda: buffer.update(
                        [
                            (
                                "inner",
                                styled(rich.table.Table)(
                                    "ID",
                                    "TAG",
                                    "CREATED",
                                    "UPDATED",
                                    "USED",
                                    "SIZE",
                                ),
                            )
                        ]
                    )
                    buffer["breathe"] = lambda: (
                        (
                            console.print(
                                buffer["inner"], style="colour.secondary"
                            ),
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
                        [
                            table["add"](next(reel))
                            for _ in range(7 if quick_draw else 6)
                        ]

                        no8 = next(reel)
                        quick_draw = False

                    except StopIteration:
                        quick_draw = True

                    finally:
                        table["breathe"]()

                        if quick_draw and not no8:
                            break

                if settings["json"]:
                    console.print_json(data={"batches": table["inner"]})

                    continue

                if table["count"]() == 0:
                    console.print("No save to show.")

                    continue

"""
- dependency level 1.
"""

from enum import Enum
from pathlib import Path
from sqlite3 import Cursor
from typing import Annotated, Any, Iterable

from rich.box import Box
from rich.table import Table
from typer import Option, Typer

from ryujinxkit.data import (
    DEFAULT_ARCHIVE_NAME,
    archive,
    collect_saves,
    create_save,
    read_archive,
    remove_save,
    retag_save,
    use_save,
)
from ryujinxkit.general import (
    DATABASE_SAVE_TAG_DEFAULT,
    UI_REFRESH_RATE,
    Session,
)

# =============================================================================


class _ListOrder(Enum):
    ID_ASC = "id+"
    TAG_ASC = "tag+"
    CREATED_ASC = "created+"
    UPDATED_ASC = "updated+"
    USED_ASC = "used+"
    SIZE_ASC = "size+"

    ID_DESC = "id-"
    TAG_DESC = "tag-"
    CREATED_DESC = "created-"
    UPDATED_DESC = "updated-"
    USED_DESC = "used-"
    SIZE_DESC = "size-"


# -----------------------------------------------------------------------------

save_commands = Typer(name="save", help="Save-usage commands.")

# -----------------------------------------------------------------------------


@save_commands.command(name="list")
def _(
    order_by: Annotated[
        list[_ListOrder],
        Option("-o", "--order-by", help="How to order your saves."),
    ] = ["used-", "updated-", "created-", "tag-", "id-"]
) -> None:
    """
    List your save instances.
    """

    cursor: Cursor

    with Session.console.status(
        status="[dim]Collecting saves",
        spinner_style="dim",
        refresh_per_second=UI_REFRESH_RATE,
    ):
        cursor = collect_saves(order_by=[lo.value for lo in order_by])

    quick_draw = True
    no8: Iterable[Any] = []

    while not quick_draw or no8 == []:
        table = Table(
            "ID",
            "TAG",
            "CREATED",
            "UPDATED",
            "USED",
            "SIZE",
            box=Box(
                box="    \n"
                "    \n"
                " -  \n"
                "    \n"
                "    \n"
                "    \n"
                "    \n"
                "    \n",
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
                (
                    Session.console.print
                    if quick_draw
                    else Session.console.input
                )(table)

            if quick_draw and no8 == []:
                break


# -----------------------------------------------------------------------------


@save_commands.command(name="create")
def _(
    tag: Annotated[
        str,
        Option(help="A tag for your save-state."),
    ] = DATABASE_SAVE_TAG_DEFAULT
) -> None:
    """
    Create an empty save state.
    """

    create_save(tag=tag)

    Session.console.print(f"ID is {Session.database_cursor.lastrowid}.")


# -----------------------------------------------------------------------------


@save_commands.command(name="remove")
def _(id_: Annotated[str, Option(help="The save-state's ID.")]) -> None:
    """
    Remove a save state.
    """

    remove_save(Session.console, id_=id_)


# -----------------------------------------------------------------------------


@save_commands.command(name="update")
def _(id_: Annotated[str, Option("--id", help="ID of save-state.")]) -> None:
    """
    Copy Ryujinx environment into a save-state.
    """

    try:
        use_save(Session.console, id_=id_, operation="update")

    except Exception:
        Session.console.print("Unknown ID.")


# -----------------------------------------------------------------------------


@save_commands.command(name="restore")
def _(id_: Annotated[str, Option("--id", help="ID of save-state.")]) -> None:
    """
    Restore your Ryujinx environment from a save-state.
    """

    try:
        use_save(Session.console, id_=id_, operation="restore")

    except Exception:
        Session.console.print("Unknown ID.")


# -----------------------------------------------------------------------------


@save_commands.command(name="retag")
def _(
    id_: Annotated[str, Option("--id", help="Save-state's ID.")],
    tag: Annotated[str, Option(help="Save-state's new tag.")],
) -> None:
    """
    Change the tag of a save-state.
    """

    retag_save(id_=id_, tag=tag)


# -----------------------------------------------------------------------------


@save_commands.command(name="export")
def _(
    output: Annotated[
        str,
        Option(help=f"Output-file's name."),
    ] = DEFAULT_ARCHIVE_NAME
) -> None:
    """
    Export your save states as a tar file.
    """

    archive(Session.console, output=output)


# -----------------------------------------------------------------------------


@save_commands.command(name="extract")
def _(path: Annotated[Path, Option(help="Path to your extract.")]) -> None:
    """
    Extract save states from an export.
    """

    try:
        Session.console.print(
            f"Accepted {
                read_archive(Session.console, path=path)
            } save instance(s).",
        )

    except FileNotFoundError:
        Session.console.print("Path is for a non-existent file.")

    except Exception:
        Session.console.print("Located file was malformed.")


# =============================================================================

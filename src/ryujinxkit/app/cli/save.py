"""
- dependency level 1.
"""

from collections.abc import Iterable
from enum import Enum
from pathlib import Path
from typing import Annotated, Any

from rich.box import Box
from rich.table import Table
from typer import Argument, Option, Typer

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
from ryujinxkit.general import DATABASE_SAVE_TAG_DEFAULT, Session

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

save_commands = Typer(help="Save-usage commands.")

# -----------------------------------------------------------------------------


@save_commands.command(name="list", epilog="Aliases: ls")
@save_commands.command(name="ls", hidden=True)
def _(
    order_by: Annotated[
        list[_ListOrder],
        Option("-k", "--key", help="Sort key."),
    ] = [
        "used-",
        "updated-",
        "created-",
        "tag-",
        "id-",
    ]  # type: ignore
) -> None:
    """
    List your save instances.
    """

    cursor = collect_saves(
        console=Session.console,
        order_by=[lo.value for lo in order_by],
    )
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
                Session.console.print(table)

                if not quick_draw:
                    Session.console.input()

            if quick_draw and no8 == []:
                break


# -----------------------------------------------------------------------------


@save_commands.command(name="create")
def _(
    tag: Annotated[
        str,
        Option(help="A tag for your save."),
    ] = DATABASE_SAVE_TAG_DEFAULT
) -> None:
    """
    Create an empty save.
    """

    create_save(tag=tag)

    Session.console.print(f"ID is {Session.database_cursor.lastrowid}.")


# -----------------------------------------------------------------------------


@save_commands.command(name="remove", epilog="Aliases: rm")
@save_commands.command(name="rm", hidden=True)
def _(
    id_: Annotated[str, Argument(metavar="ID", help="The save's ID.")]
) -> None:
    """
    Remove a save.
    """

    remove_save(console=Session.console, id_=id_)


# -----------------------------------------------------------------------------


@save_commands.command(name="update")
def _(
    id_: Annotated[str, Argument(metavar="ID", help="ID of save-state.")]
) -> None:
    """
    Copy Ryujinx environment into a save.
    """

    try:
        use_save(console=Session.console, id_=id_, operation="update")

    except Exception:
        Session.console.print("Unknown ID.")


# -----------------------------------------------------------------------------


@save_commands.command(name="restore")
def _(id_: Annotated[str, Argument(metavar="ID", help="Save's ID.")]) -> None:
    """
    Restore your Ryujinx environment from save.
    """

    try:
        use_save(console=Session.console, id_=id_, operation="restore")

    except Exception:
        Session.console.print("Unknown ID.")


# -----------------------------------------------------------------------------


@save_commands.command(name="retag", epilog="Aliases: rt")
@save_commands.command(name="rt", hidden=True)
def _(
    id_: Annotated[str, Argument(metavar="ID", help="Save's ID.")],
    tag: Annotated[str, Argument(metavar="TAG", help="Save's new tag.")],
) -> None:
    """
    Change a save's tag.
    """

    retag_save(id_=id_, tag=tag)


# -----------------------------------------------------------------------------


@save_commands.command(name="export")
def _(
    output: Annotated[
        Path,
        Option(help="Output-file's path."),
    ] = Path(DEFAULT_ARCHIVE_NAME)
) -> None:
    """
    Export your saves to a tar file.
    """

    archive(console=Session.console, output=output)


# -----------------------------------------------------------------------------


@save_commands.command(name="extract")
def _(
    path: Annotated[
        Path,
        Argument(
            metavar="PATH",
            exists=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to your extract.",
        ),
    ]
) -> None:
    """
    Extract saves from an export.
    """

    try:
        Session.console.print(
            f"Accepted {
                read_archive(console=Session.console, path=path)
            } save instance(s).",
        )

    except Exception:
        Session.console.print("Located file was malformed.")


# =============================================================================

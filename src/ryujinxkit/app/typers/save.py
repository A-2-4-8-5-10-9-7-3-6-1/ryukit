"""
- dependency level 1.
"""

import collections.abc
import enum
import pathlib
import typing

import rich.box
import rich.table
import typer

import ryujinxkit.data
import ryujinxkit.general

from ..objects import Objects

save = typer.Typer(help="Save-usage commands.")


class _ListOrder(str, enum.Enum):
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


@save.command(name="list", epilog="Aliases: ls")
@save.command(name="ls", hidden=True)
def _(
    order_by: typing.Annotated[
        list[_ListOrder],
        typer.Option("-k", "--key", help="Sort key."),
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

    cursor = ryujinxkit.data.collect_saves(
        console=Objects.console, order_by=[lo.value for lo in order_by]
    )
    quick_draw = True
    no8: collections.abc.Iterable[typing.Any] = []

    while not quick_draw or no8 == []:
        table = rich.table.Table(
            "ID",
            "TAG",
            "CREATED",
            "UPDATED",
            "USED",
            "SIZE",
            box=rich.box.Box(
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
                Objects.console.print(table)

                if not quick_draw:
                    Objects.console.input()

            if quick_draw and no8 == []:
                break


@save.command(name="create")
def _(
    tag: typing.Annotated[
        str,
        typer.Option(help="A tag for your save."),
    ] = ryujinxkit.general.DATABASE_SAVE_TAG_DEFAULT
) -> None:
    """
    Create an empty save.
    """

    ryujinxkit.data.create_save(tag=tag)

    Objects.console.print(
        f"ID is {
            ryujinxkit.general.Session.database_cursor.lastrowid
        }."
    )


@save.command(name="remove", epilog="Aliases: rm")
@save.command(name="rm", hidden=True)
def _(
    id_: typing.Annotated[
        str,
        typer.Argument(metavar="ID", help="The save's ID."),
    ]
) -> None:
    """
    Remove a save.
    """

    ryujinxkit.data.remove_save(console=Objects.console, id_=id_)


@save.command(name="update")
def _(
    id_: typing.Annotated[
        str,
        typer.Argument(metavar="ID", help="ID of save-state."),
    ]
) -> None:
    """
    Copy Ryujinx environment into a save.
    """

    try:
        ryujinxkit.data.use_save(
            console=Objects.console,
            id_=id_,
            operation="update",
        )

    except Exception:
        Objects.console.print("Unknown ID.")


@save.command(name="restore")
def _(
    id_: typing.Annotated[str, typer.Argument(metavar="ID", help="Save's ID.")]
) -> None:
    """
    Restore your Ryujinx environment from save.
    """

    try:
        ryujinxkit.data.use_save(
            console=Objects.console,
            id_=id_,
            operation="restore",
        )

    except Exception:
        Objects.console.print("Unknown ID.")


@save.command(name="retag", epilog="Aliases: rt")
@save.command(name="rt", hidden=True)
def _(
    id_: typing.Annotated[
        str,
        typer.Argument(metavar="ID", help="Save's ID."),
    ],
    tag: typing.Annotated[
        str,
        typer.Argument(metavar="TAG", help="Save's new tag."),
    ],
) -> None:
    """
    Change a save's tag.
    """

    ryujinxkit.data.retag_save(id_=id_, tag=tag)


@save.command(name="export")
def _(
    output: typing.Annotated[
        pathlib.Path,
        typer.Option(help="Output-file's path."),
    ] = pathlib.Path(ryujinxkit.data.DEFAULT_ARCHIVE_NAME)
) -> None:
    """
    Export your saves to a tar file.
    """

    ryujinxkit.data.archive(console=Objects.console, output=output)


@save.command(name="extract")
def _(
    path: typing.Annotated[
        pathlib.Path,
        typer.Argument(
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
        Objects.console.print(
            f"Accepted {
                ryujinxkit.data.read_archive(console=Objects.console, path=path)
            } save instance(s).",
        )

    except Exception:
        Objects.console.print("Located file was malformed.")

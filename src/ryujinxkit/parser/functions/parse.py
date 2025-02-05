"""
- dependency level 1.
"""

from argparse import Namespace
from os import getenv
from pathlib import Path
from typing import Any, Callable, Iterable

from parser_generator import Command, generate
from requests import ConnectionError
from rich.box import Box
from rich.table import Table

from ryujinxkit.data import (
    archive,
    read_archive,
    remove_save,
    source,
    use_save,
)
from ryujinxkit.general import (
    APP_VERSION,
    DATABASE_SAVE_TAG_DEFAULT,
    FileNode,
    Session,
)

from ..constants.configs import DEFAULT_ARCHIVE_NAME

# =============================================================================

_configs: dict[Callable[[Namespace], Any], Command] = {}

# -----------------------------------------------------------------------------


def _command(
    formatters: list[tuple[str, Callable[[Any], Any]]] = [],
    **kwargs: Any,
) -> Callable[[Callable[[Namespace], Any]], Callable[[Namespace], Any]]:
    """
    Add command configuration to `_configs`.

    **Notes**:
        - Settings for `defaults["func"]` will be overwritten by whatever \
        function proceeds this decorator.
        - For the root command, do not set `parent`.

    :param formatters: Formatters for the command.
    :param kwargs: Parameters from `parser_generator.Command`.

    :returns: Adder for setting the function key in `defaults`.
    """

    kwargs.setdefault("defaults", {})

    def inner(
        function: Callable[[Namespace], Any]
    ) -> Callable[[Namespace], Any]:
        kwargs["defaults"]["func"] = lambda namespace: [
            [
                setattr(namespace, key, sanitizer(getattr(namespace, key)))
                for key, sanitizer in formatters
            ],
            function(namespace),
        ][1]

        kwargs.setdefault("parent", kwargs["defaults"]["func"])

        _configs[kwargs["defaults"]["func"]] = Command(**kwargs)

        return kwargs["defaults"]["func"]

    return inner


# -----------------------------------------------------------------------------


def _format_tag(tag: str) -> str:
    """
    Format save-state tag.

    :param tag: Tag to be formatted.

    :returns: Formatted tag.
    """

    if tag != "" and tag[0].isalnum():
        return tag.strip().replace(" ", "-").lower()

    return DATABASE_SAVE_TAG_DEFAULT


# -----------------------------------------------------------------------------


@_command(
    parser_args={
        "prog": "ryujinxkit",
        "description": "A tool for Ryujinx (for Windows) " "management.",
    },
    subparsers_args={
        "title": "commands",
    },
    params=[
        (
            ["--version"],
            {
                "help": "Show version and quit",
                "action": "store_true",
            },
        )
    ],
)
def _ryujinxkit(args: Namespace) -> None:
    if args.version:
        Session.console.print(f"RyujinxKit version {APP_VERSION}.")

    else:
        Session.console.print("Try using '--help'.")


# -----------------------------------------------------------------------------


@_command(
    parser_args={
        "name": "save",
        "help": "Save-state usage commands",
        "aliases": ["sv"],
    },
    subparsers_args={
        "title": "commands",
        "required": True,
    },
    parent=_ryujinxkit,
)
def _ryujinxkit_save(_: Namespace) -> None:
    pass


# -----------------------------------------------------------------------------


@_command(
    parser_args={
        "name": "list",
        "help": "List your save instances",
        "aliases": ["ls"],
    },
    parent=_ryujinxkit_save,
    params=[
        (
            ["--order-by"],
            {
                "help": "Priority ordering for rows",
                "choices": (
                    lambda bin, options: [
                        [bin.extend([f"{x}+", f"{x}-"]) for x in options],
                        bin,
                    ][1]
                )([], ["id", "tag", "created", "updated", "used", "size"]),
                "nargs": "+",
            },
        ),
    ],
    defaults={
        "order_by": ["used-", "updated-", "created-"],
    },
)
def _ryujinxkit_save_list(args: Namespace) -> None:
    with Session.console.status(
        status="[dim]Collecting saves",
        spinner_style="dim",
    ):
        Session.database_cursor.execute(
            f"""
            SELECT 
                CAST(id AS TEXT),
                CAST(tag AS TEXT),
                CAST(strftime("%Y/%m/%d %H:%M", created) AS TEXT),
                CAST(strftime("%Y/%m/%d %H:%M", updated) AS TEXT),
                CAST(strftime("%Y/%m/%d %H:%M", used) AS TEXT),
                CAST(ROUND(size / (1024 * 1024.0), 2) AS TEXT) || "MB"
            FROM (
                SELECT id, tag, created, updated, used, size
                FROM saves
                ORDER BY {
                    ", ".join(
                        f"{flag[:-1]} {"DESC" if flag[-1] == "-" else "ASC"}"
                        for flag in args.order_by
                    )
                }
            )
            """
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
                table.add_row(*next(Session.database_cursor))
                for _ in range(7 if quick_draw else 6)
            ]

            no8 = next(Session.database_cursor)
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


@_command(
    parser_args={
        "name": "install",
        "description": "You must set a service url through '--url' or "
        "the environment variable RYUJINXKIT_SERVICE_URL.",
        "help": "Install and ready Ryujinx.",
        "aliases": ["source"],
    },
    params=[
        (
            ["--url"],
            {
                "help": "Download URL (aquired from an authority)",
                "type": str,
            },
        )
    ],
    parent=_ryujinxkit,
    defaults={
        "url": getenv(key="RYUJINXKIT_SERVICE_URL"),
    },
)
def _ryujinxkit_install(args: Namespace) -> None:
    try:
        source(Session.console, url=args.url)

        Session.console.print(
            "Installed to",
            f"{Session.resolver(id_=FileNode.RYUJINX_LOCAL_DATA)}.",
        )

    except ConnectionError:
        Session.console.print("Failed to connect to service.")

    except Exception:
        Session.console.print(
            "An error occured. This was the resullt of one of the "
            "following:\n",
            "(1) Your URL locates an invalid service,",
            "(2) Your connection timed out.",
            "\nIn case of (1), contact an authority for a valid URL.",
            sep="\n",
        )


# -----------------------------------------------------------------------------


@_command(
    formatters=[("tag", _format_tag)],
    parser_args={
        "name": "create",
        "help": "Create a new save state--it will be empty",
    },
    params=[
        (
            ["-t", "--tag"],
            {
                "help": "A tag for your save state",
                "type": str,
            },
        )
    ],
    parent=_ryujinxkit_save,
    defaults={
        "tag": DATABASE_SAVE_TAG_DEFAULT,
    },
)
def _ryujinxkit_save_create(args: Namespace) -> None:
    Session.database_cursor.execute(
        """
        INSERT INTO saves (tag)
        VALUES (?);
        """,
        [args.tag],
    )

    Session.console.print(f"ID is {Session.database_cursor.lastrowid}.")


# -----------------------------------------------------------------------------


@_command(
    parser_args={
        "name": "remove",
        "aliases": ["rm"],
        "help": "Remove a save state",
    },
    params=[
        {
            "help": "The save-state's ID",
            "type": str,
            "dest": "id",
        }
    ],
    parent=_ryujinxkit_save,
)
def _ryujinxkit_save_remove(args: Namespace) -> None:
    remove_save(Session.console, id_=args.id)


# -----------------------------------------------------------------------------


@_command(
    parser_args={
        "name": "update",
        "help": "Update a save state with the current "
        "environment of your Ryujinx installation",
    },
    params=[
        {
            "dest": "id",
            "help": "ID of save state",
            "type": str,
        }
    ],
    parent=_ryujinxkit_save,
)
def _ryujinxkit_save_update(args: Namespace) -> None:
    try:
        use_save(Session.console, id_=args.id, operation="update")

    except Exception:
        Session.console.print("Unknown ID.")


# -----------------------------------------------------------------------------


@_command(
    parser_args={
        "name": "restore",
        "help": "Restore your Ryujinx environment from a save state",
    },
    params=[
        {
            "dest": "id",
            "help": "ID of save state",
            "type": str,
        }
    ],
    parent=_ryujinxkit_save,
)
def _ryujinxkit_save_restore(args: Namespace) -> None:
    try:
        use_save(Session.console, id_=args.id, operation="restore")

    except Exception:
        Session.console.print("Unknown ID.")


# -----------------------------------------------------------------------------


@_command(
    formatters=[("tag", _format_tag)],
    parser_args={
        "name": "retag",
        "help": "Change the tag of a save-state",
        "aliases": ["rt"],
    },
    params=[
        {
            "help": "Save-state's ID",
            "dest": "id",
            "type": str,
        },
        {
            "dest": "tag",
            "type": str,
            "help": "A new tag for the save state",
        },
    ],
    parent=_ryujinxkit_save,
)
def _ryujinxkit_save_retag(args: Namespace) -> None:
    Session.database_cursor.execute(
        """
        UPDATE saves
        SET tag = ?, updated = datetime("now")
        WHERE id = ?;
        """,
        [args.tag, args.id],
    )


# -----------------------------------------------------------------------------


@_command(
    formatters=[
        (
            "output",
            lambda name: name if name != "" else DEFAULT_ARCHIVE_NAME,
        )
    ],
    parser_args={
        "name": "export",
        "help": "Export your save states as a tar file",
        "aliases": ["archive"],
    },
    params=[
        (
            ["-o", "--output"],
            {
                "help": f"Output-file name--default is {DEFAULT_ARCHIVE_NAME}",
                "type": str,
            },
        )
    ],
    parent=_ryujinxkit_save,
    defaults={
        "output": DEFAULT_ARCHIVE_NAME,
    },
)
def _ryujinxkit_save_export(args: Namespace) -> None:
    archive(Session.console, output=args.output)


# -----------------------------------------------------------------------------


@_command(
    parser_args={
        "name": "extract",
        "help": "Extract save states from an export",
        "aliases": ["read"],
    },
    params=[
        {
            "dest": "path",
            "help": "Path to your extract",
            "type": Path,
        }
    ],
    parent=_ryujinxkit_save,
)
def _ryujinxkit_save_extract(args: Namespace) -> None:
    try:
        Session.console.print(
            "Accepted",
            read_archive(Session.console, path=args.path),
            "save instance(s).",
        )

    except FileNotFoundError:
        Session.console.print("Path is for a non-existent file.")

    except Exception:
        Session.console.print("Located file was malformed.")


# -----------------------------------------------------------------------------

parse = generate(function_attr="func", commands=_configs)[1]

# =============================================================================

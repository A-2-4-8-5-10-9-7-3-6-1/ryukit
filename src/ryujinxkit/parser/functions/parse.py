"""
- dependency level 0.
"""

from argparse import Namespace
from pathlib import Path
from typing import Any, Callable

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
    DATABASE_SAVE_TAG_DEFAULT,
    RYUJINXKIT_NAME,
    RYUJINXKIT_VERSION,
    FileNode,
    RyujinxKitCommand,
    Session,
)

from ..constants.configs import DEFAULT_ARCHIVE_NAME

# =============================================================================

_configs: dict[RyujinxKitCommand, Command] = {}

# -----------------------------------------------------------------------------


def _command(
    id_: RyujinxKitCommand,
    formatters: list[tuple[str, Callable[[Any], Any]]] = [],
    **kwargs: Any,
) -> Callable[[Callable[[Namespace], Any]], None]:
    """
    Add command configuration to `_configs`.

    **Notes**:
        - Settings for `defaults["func"]` will be overwritten by whatever \
        function proceeds this decorator.

    :param %id_%: Command's ID.
    :param formatters: Formatters for the command.
    :param kwargs: Parameters from `parser_generator.Command`.

    :returns: Adder for setting the function key in `defaults`.
    """

    kwargs.setdefault("defaults", {})

    def inner(function: Callable[[Namespace], Any]) -> None:
        kwargs["defaults"]["func"] = lambda namespace: [
            [
                setattr(namespace, key, sanitizer(getattr(namespace, key)))
                for key, sanitizer in formatters
            ],
            function(namespace),
        ][1]

        _configs[id_] = Command(**kwargs)

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
    id_=RyujinxKitCommand.RYUJINXKIT_SOURCE,
    parser_args={
        "name": "install",
        "help": "Install and ready Ryujinx",
        "aliases": ["source"],
    },
    params=[
        {
            "dest": "url",
            "help": "Download URL (obtained from an authority)",
            "type": str,
        }
    ],
    parent=RyujinxKitCommand.RYUJINXKIT,
)
def _(args: Namespace) -> None:
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
    id_=RyujinxKitCommand.RYUJINXKIT_SAVE_CREATE,
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
    parent=RyujinxKitCommand.RYUJINXKIT_SAVE,
    defaults={
        "tag": DATABASE_SAVE_TAG_DEFAULT,
    },
)
def _(args: Namespace) -> None:
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
    id_=RyujinxKitCommand.RYUJINXKIT_SAVE_REMOVE,
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
    parent=RyujinxKitCommand.RYUJINXKIT_SAVE,
)
def _(args: Namespace) -> None:
    remove_save(Session.console, id_=args.id)


# -----------------------------------------------------------------------------


@_command(
    id_=RyujinxKitCommand.RYUJINXKIT_SAVE_UPDATE,
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
    parent=RyujinxKitCommand.RYUJINXKIT_SAVE,
)
def _(args: Namespace) -> None:
    try:
        use_save(Session.console, id_=args.id, operation="update")

    except Exception:
        Session.console.print("Unknown ID.")


# -----------------------------------------------------------------------------


@_command(
    id_=RyujinxKitCommand.RYUJINXKIT_SAVE_RESTORE,
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
    parent=RyujinxKitCommand.RYUJINXKIT_SAVE,
)
def _(args: Namespace) -> None:
    try:
        use_save(Session.console, id_=args.id, operation="restore")

    except Exception:
        Session.console.print("Unknown ID.")


# -----------------------------------------------------------------------------


@_command(
    id_=RyujinxKitCommand.RYUJINXKIT_SAVE_RETAG,
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
    parent=RyujinxKitCommand.RYUJINXKIT_SAVE,
)
def _(args: Namespace) -> None:
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
    id_=RyujinxKitCommand.RYUJINXKIT_SAVE_EXPORT,
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
    parent=RyujinxKitCommand.RYUJINXKIT_SAVE,
    defaults={
        "output": DEFAULT_ARCHIVE_NAME,
    },
)
def _(args: Namespace) -> None:
    archive(Session.console, output=args.output)


# -----------------------------------------------------------------------------


@_command(
    id_=RyujinxKitCommand.RYUJINXKIT_SAVE_EXTRACT,
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
    parent=RyujinxKitCommand.RYUJINXKIT_SAVE,
)
def _(args: Namespace) -> None:
    try:
        Session.console.print(
            "Added",
            read_archive(Session.console, path=args.path),
            "save instances (instance).",
        )  # change to "collected ... instance(s) from extraction."

    except FileNotFoundError:
        Session.console.print("Path is for a non-existent file.")

    except Exception:
        Session.console.print("Located file was malformed.")


# -----------------------------------------------------------------------------


@_command(
    id_=RyujinxKitCommand.RYUJINXKIT,
    parser_args={
        "prog": RYUJINXKIT_NAME.lower(),
        "description": "A tool for Ryujinx (for Windows) " "management.",
    },
    subparsers_args={
        "title": "commands",
    },
    parent=RyujinxKitCommand.RYUJINXKIT,
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
def _(args: Namespace) -> None:
    if args.version:
        Session.console.print(
            f"{RYUJINXKIT_NAME} version {RYUJINXKIT_VERSION}"
        )

    else:
        Session.console.print("Try using '--help'.")


# -----------------------------------------------------------------------------


@_command(
    id_=RyujinxKitCommand.RYUJINXKIT_SAVE,
    parser_args={
        "name": "save",
        "help": "Save-state usage commands",
        "aliases": ["sv"],
    },
    subparsers_args={
        "title": "commands",
    },
    parent=RyujinxKitCommand.RYUJINXKIT,
    params=[
        (
            ["--list"],
            {
                "help": "List your save instances.",
                "action": "store_true",
            },
        ),
    ],
)
def _(args: Namespace) -> None:
    if args.list:
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

        [
            table.add_row(*row)
            for row in Session.database_cursor.execute(
                """
                SELECT 
                    CAST(id AS TEXT),
                    CAST(tag AS TEXT),
                    CAST(strftime("%Y/%m/%d %H:%M", created) AS TEXT),
                    CAST(strftime("%Y/%m/%d %H:%M", updated) AS TEXT),
                    CAST(strftime("%Y/%m/%d %H:%M", updated) AS text),
                    CAST(ROUND(size / (1024 * 1024.0), 2) AS TEXT) || "MB"
                FROM saves
                ORDER BY used DESC, updated DESC, created DESC;
                """
            ).fetchall()
        ]

        with Session.console.pager():
            Session.console.print(table)

    else:
        Session.console.print("Try using '--help'.")


# -----------------------------------------------------------------------------

parse = generate(function_attr="func", commands=_configs)[1]

# =============================================================================

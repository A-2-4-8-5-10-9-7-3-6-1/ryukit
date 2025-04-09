"""Utilities for typer construction."""

import collections
import collections.abc
import importlib
import importlib.resources
import pathlib
import typing

import typer

from ..core import ui

__all__ = ["build_typer", "TyperBuilderArgs"]


class TyperBuilderArgs(typing.TypedDict, total=False):
    typer_args: collections.abc.Collection[
        collections.abc.Mapping[str, object]
    ]
    command: collections.abc.Callable[..., object]


def build_typer(base: str, *fragments: str):
    """
    Builds a typer from a well-structured directory.

    :param base: Base fragment of internal path to a well-structured directory.
    :param fragments: Path fragments to append onto the base fragmenet.

    :returns: A typer corresponding to the targeted directory.

    Instructions
    ------------

    This tool allows for file-based CLI routing, meaning that the structure of the resulting CLI tool is dynamically determined by the file structure of whichever directory is given via `path`. A well-structured directory is one in which every file is a module that exports a typer.Typer instance named 'app'. parser_.py files define subtypers, and their 'app' exports should be configured as such. .py files, other than parser_.py, will have their 'app' export hooked onto the nearest 'app' instance from a parser_.py file.

    Note
    ----
    Using this function to build a typer on every app startup might result in slowdowns. Look for ways to cache the build, or return to static importing.
    """

    root = ["ryukit", base, *fragments]
    stack: list[tuple[typer.Typer | None, list[list[str]]]] = [(None, [root])]
    special_files = {"typer_definition": "parser_.py"}
    app: typer.Typer | None = None
    path: pathlib.Path
    entry: str
    prefix: list[str]
    FileProcessor = typing.TypedDict(
        "FileProcessor",
        {
            "adder": collections.abc.Callable[
                [
                    collections.abc.Callable[..., object],
                    collections.abc.Mapping[str, typing.Any],
                ],
                object,
            ],
            "break": bool,
        },
    )

    def parser_adder(
        command: collections.abc.Callable[..., object],
        kwargs: collections.abc.Mapping[str, typing.Any],
    ):
        if path.stem == special_files["typer_definition"] and stack[-1][0]:
            raise RuntimeError(
                f"Attempted to add a Typer multiple times in {path}, a Typer cannot have aliases."
            )

        parser = ui.theme_applier(typer.Typer)(
            **typing.cast(
                dict[str, typing.Any],
                {"name": path.parent.stem.replace("_", "-"), **kwargs},
            )
        )
        stack[-1] = (parser, stack[-1][1])

        if len(stack) == 1:
            return

        typing.cast(typer.Typer, stack[-2][0]).add_typer(
            parser, callback=command
        )

    while stack:
        app, entries = stack[-1]

        if not entries or entries[0] == root:
            stack.pop()

        while entries:
            *prefix, entry = entries.pop(0)
            path = pathlib.Path(*prefix, entry)

            if entry.endswith(".py"):
                module = importlib.import_module(
                    ".".join((*prefix, entry[:-3]))
                )
                processor: FileProcessor = (
                    {"adder": parser_adder, "break": True}
                    if entry == special_files["typer_definition"]
                    else {
                        "adder": lambda command, kwargs: typing.cast(
                            typer.Typer, app
                        ).command(
                            **typing.cast(
                                dict[str, typing.Any],
                                {
                                    "name": entry[:-3].replace("_", "-"),
                                    **kwargs,
                                },
                            )
                        )(
                            command
                        ),
                        "break": False,
                    }
                )

                if not hasattr(module, "typer_builder_args"):
                    continue

                args: TyperBuilderArgs = module.typer_builder_args

                args.setdefault("typer_args", [])

                args["typer_args"] = typing.cast(
                    collections.abc.Collection[
                        collections.abc.Mapping[str, object]
                    ],
                    args.get("typer_args"),
                )

                if len(args["typer_args"]) == 0:
                    args["typer_args"] = [{}]

                for options in args["typer_args"]:
                    processor["adder"](
                        args.get("command", lambda: None), options
                    )

                if processor["break"]:
                    break

                continue

            pending_entries: list[list[str]] = []

            for new_entry in importlib.resources.contents(*prefix, entry):
                pending_entries.insert(
                    (
                        0
                        if new_entry == special_files["typer_definition"]
                        else (
                            1
                            if new_entry.endswith(".py")
                            else len(pending_entries)
                        )
                    ),
                    [*prefix, entry, new_entry],
                )

            if (
                pending_entries
                and pending_entries[0][-1] == special_files["typer_definition"]
            ):
                stack.append((None, pending_entries))

                break

            elif app is None:
                raise RuntimeError(f"No root Typer at {path}.")

            entries.extend(pending_entries)

    return typing.cast(typer.Typer, app)

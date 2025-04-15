"""Utilities for typer construction."""

import collections
import collections.abc
import importlib
import importlib.resources
import pathlib
import typing

import typer

from ..core import presentation

__all__ = ["build", "TyperBuilderArgs"]


class TyperBuilderArgs(typing.TypedDict, total=False):
    typer_args: collections.abc.Collection[
        collections.abc.Mapping[str, object]
    ]
    command: collections.abc.Callable[..., object]


def build(base: str, *fragments: str):
    """
    Builds a typer from a well-structured directory.

    This tool allows for file-based CLI routing, meaning that the structure of the resulting typer object's commands will resemble that of the files within the indicated directory. Those file which are required for the CLI must export a 'typer_builder_args' variable, and they are processed as follows:

    - __typer__.py files: These files indicate typers and sub-typers in the CLI. Within 'typer_builder_args': 'command' defines a callback of the typer, while 'typer_args' is a collection containing up to one dict entry --- arguments to forward to the `typer.Typer` invocation.
    - Other .py files: These files define leaf-level commands for the CLI. Each will be placed under their *nearest* typer instance, the one corresponding to the most-immediate directory containing a __typer__.py file. The 'command' field in 'typer_builder_args' will be the implementation of the command, whilst the 'typer_args' field will be a collection of dicts --- each providing arguments for a `typer.Typer.command` call, and each representing an alias for the same command.

    Note that if in either case 'typer_args' is excluded from 'typer_builder_args', or no entry in 'typer_args' contains a 'name' field, then the spawned object will be given a name that reflects that of the file it's defined in.

    :param base: Base fragment of internal path to a well-structured directory.
    :param fragments: Path fragments to append onto the base fragment.

    :returns: A typer corresponding to the targeted directory.

    :raises RuntimeError: If the provided directory has no immediate __typer__.py file.
    :raises RuntimeError: If aliasing is attempted in a __typer__.py file.
    """

    root = ["ryukit", base, *fragments]
    stack: list[tuple[typer.Typer | None, list[list[str]]]] = [(None, [root])]
    special_files = {"typer_definition": "__typer__.py"}
    app: typer.Typer | None = None
    null_command = lambda: None
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

    def typer_adder(
        command: collections.abc.Callable[..., object],
        kwargs: collections.abc.Mapping[str, typing.Any],
    ):
        if path.stem == special_files["typer_definition"] and stack[-1][0]:
            raise RuntimeError(
                f"Attempted to aliase in {path}. A Typer cannot have aliases."
            )

        parser = presentation.theme_applier(typer.Typer)(
            **typing.cast(
                dict[str, typing.Any],
                {"name": path.parent.stem.replace("_", "-"), **kwargs},
            ),
            callback=command,
        )
        stack[-1] = (parser, stack[-1][1])

        if len(stack) == 1:
            return

        typing.cast(typer.Typer, stack[-2][0]).add_typer(parser)

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
                    {"adder": typer_adder, "break": True}
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
                args["typer_args"] = typing.cast(
                    collections.abc.Collection[
                        collections.abc.Mapping[str, object]
                    ],
                    args.get("typer_args", []),
                )

                if len(args["typer_args"]) == 0:
                    args["typer_args"] = [{}]

                for alias in args["typer_args"]:
                    processor["adder"](
                        args.get("command", null_command), alias
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
                raise RuntimeError(f"Missing root Typer at {path}.")

            entries.extend(pending_entries)

    return typing.cast(typer.Typer, app)

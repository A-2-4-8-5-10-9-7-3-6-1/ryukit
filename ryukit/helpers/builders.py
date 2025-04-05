"""App-building utilities."""

import importlib
import importlib.resources
import pathlib
import typing

import typer

__all__ = ["typer_from_dir"]

# ==== FS-Typer Routing ====

# NOTE: Using this function to build a typer on every app startup might result in slowdowns. Look for ways to cache the build, or return to static importing.


def typer_from_dir(base: str, *fragments: str):
    """
    Builds a typer from a well-structured directory.

    :param base: Base fragment of internal path to a well-structured directory.
    :param fragments: Path fragments to append onto the base fragmenet.

    :returns: A typer corresponding to the targeted directory.

    Instructions
    ------------

    This tool allows for file-based CLI routing, meaning that the structure of the resulting CLI tool is dynamically determined by the file structure of whichever directory is given via `path`. A well-structured directory is one in which every file is a module that exports a typer.Typer instance named 'app'. parser_.py files define subtypers, and their 'app' exports should be configured as such. .py files, other than parser_.py, will have their 'app' export hooked onto the nearest 'app' instance from a parser_.py file.
    """

    root = ("ryukit", base, *fragments)
    stack: list[tuple[typer.Typer | None, list[tuple[str, ...]]]] = [
        (None, [root])
    ]
    special_files = {"typer_definition": "parser_.py"}
    app: typer.Typer | None = None

    while stack:
        app, entries = stack[-1]

        if not entries or entries[0] == root:
            stack.pop()

        while entries:
            *prefix, entry = entries.pop(0)

            if entry.endswith(".py"):
                module = importlib.import_module(
                    ".".join((*prefix, entry[:-3]))
                )
                parent = app

                if not hasattr(module, "app"):
                    raise RuntimeError(
                        f"Missing 'app' typer in {pathlib.Path(*prefix, entry)}."
                    )

                if entry == special_files["typer_definition"]:
                    stack[-1] = (module.app, entries)
                    app = stack[-1][0]

                    if len(stack) < 2:
                        break

                    parent = stack[-2][0]

                typing.cast(typer.Typer, parent).add_typer(module.app)

                continue

            pending_entries: list[tuple[str, ...]] = []

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
                    (*prefix, entry, new_entry),
                )

            if (
                pending_entries
                and pending_entries[0][-1] == special_files["typer_definition"]
            ):
                stack.append((None, pending_entries))

                break

            elif app is None:
                raise RuntimeError(
                    f"No root typer at {pathlib.Path(*prefix, entry)}."
                )

            entries.extend(pending_entries)

    return typing.cast(typer.Typer, app)

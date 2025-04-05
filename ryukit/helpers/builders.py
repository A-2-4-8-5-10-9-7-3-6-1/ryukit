"""Build utilities."""

import importlib
import importlib.resources
import typing

import typer

__all__ = ["typer_from_dir"]

# ==== FS-Typer routing ====


def typer_from_dir(*path: str):
    """
    Builds a typer from a well-structured directory.

    :param path: Internal path to the well-structured directory.

    :returns: A typer corresponding to the targeted directory.
    """

    typers: list[
        tuple[typer.Typer | None, list[tuple[str, ...]], *tuple[str, ...]]
    ] = [(None, [path], "ryukit")]
    special_files = {"typer_definition": "parser_.py"}
    app: typer.Typer | None = None

    while typers:
        app, span, *app_path = typers[-1]

        if not span or len(app_path) == 1:
            typers.pop()

        while span:
            *file_path, file = span.pop(0)

            if file == special_files["typer_definition"]:
                try:
                    typers[-1] = (
                        importlib.import_module(
                            ".".join((*app_path, *file_path, file[:-3]))
                        ).app,
                        span,
                        *app_path,
                    )

                    app = typers[-1][0]

                    if len(typers) < 2:
                        continue

                    typing.cast(typer.Typer, typers[-2][0]).add_typer(
                        typing.cast(typer.Typer, app)
                    )

                except AttributeError as e:
                    raise RuntimeError(
                        "Expected export of typer variable 'app'."
                    ) from e

                continue

            if file.endswith(".py"):
                try:
                    typing.cast(typer.Typer, app).add_typer(
                        importlib.import_module(
                            ".".join((*app_path, *file_path, file[:-3]))
                        ).app
                    )

                except AttributeError as e:
                    raise RuntimeError(
                        "Expected export of typer variable 'app'."
                    ) from e

                continue

            files: list[tuple[str, ...]] = []

            for item in importlib.resources.contents(
                *app_path, *file_path, file
            ):
                files.insert(
                    (
                        0
                        if item == special_files["typer_definition"]
                        else 1 if item.endswith(".py") else len(files)
                    ),
                    (item,),
                )

            if not files or files[0][0] != special_files["typer_definition"]:
                span.extend((*file_path, file, *item) for item in files)

                continue

            typers.append((None, files, *app_path, file))

            break

    if not app:
        raise Exception("Root parser not found.")

    return app

import importlib
import importlib.metadata
import importlib.resources
import json
import sqlite3
import typing

import jsonschema
import typer

from ...core import db, fs, ui
from ..modules import context

__all__ = []


@context.root_typer.callback(invoke_without_command=True)
def _(
    ctx: typer.Context,
    show_configs: typing.Annotated[
        bool, typer.Option("--configs", help="Show configurations and exit.")
    ] = False,
):
    "CLI for managing Ryujinx (on Windows)."

    [
        folder().mkdir(parents=True, exist_ok=True)
        for folder in [fs.File.ROAMING_APP_DATA]
    ]

    if not fs.File.CONFIG_FILE().exists():
        with fs.File.CONFIG_FILE().open("w") as buffer:
            json.dump(
                {
                    k: v
                    for k, v in json.loads(
                        (
                            importlib.resources.files("ryukit")
                            / "assets"
                            / "configs"
                            / "app-defaults.json"
                        ).read_bytes()
                    ).items()
                    if k != "$schema"
                },
                fp=buffer,
            )

    context.states.configs = json.loads(fs.File.CONFIG_FILE().read_bytes())

    try:
        typing.cast(
            typing.Any,
            jsonschema.Draft7Validator(
                json.loads(
                    (
                        importlib.resources.files("ryukit")
                        / "assets"
                        / "schemas"
                        / "app-configs.json"
                    ).read_bytes()
                )
            ),
        ).validate(context.states.configs)

    except jsonschema.ValidationError as e:

        ui.app_console.print(
            f"[error]Malformed configuration file at {e.json_path}: {e.message}."
        )

        raise typer.Exit(1)

    with db.theme_applier(sqlite3.connect)("DATABASE") as conn:
        conn.executescript(
            (
                importlib.resources.files("ryukit")
                / "assets"
                / "database-setup.sql"
            ).read_text()
        )

    for do, command in [
        (
            show_configs,
            lambda: ui.app_console.print_json(data=context.states.configs),
        ),
        (
            not ctx.invoked_subcommand,
            lambda: ui.app_console.print(
                f"[reset][colour.primary]{
                    (
                        importlib.resources.files("ryukit")
                        / "assets"
                        / "art"
                        / "logo.txt"
                    ).read_text()
                }",
                f"VERSION {importlib.metadata.version("ryukit")}",
                sep="\n\n",
                end="\n\n",
                new_line_start=True,
            ),
        ),
    ]:
        if not do:
            continue

        command()

        raise typer.Exit()

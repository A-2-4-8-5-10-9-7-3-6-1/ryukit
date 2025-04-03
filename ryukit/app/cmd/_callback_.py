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
    "A CLI tool for Ryujinx."

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

    for *key, default in [
        (
            "ryujinxConfigs",
            "distDir",
            str(
                fs.File.LOCAL_DATA_DIR()
                / "Ryujinx-{appVersion}-{targetSystem}"
            ),
        ),
        (
            "ryujinxConfigs",
            "roamingDataDir",
            str(fs.File.ROAMING_DATA_DIR() / "Ryujinx"),
        ),
    ]:
        setting: dict[str, object] = context.states.configs
        *prefix, suffix = key

        for part in prefix:
            setting = typing.cast(typing.Any, setting[part])

        setting[suffix] = setting.get(suffix, None) or default

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

        ui.console.print(
            f"[error]Malformed configuration file: {e.message}, at {e.json_path}."
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
            lambda: ui.console.print_json(data=context.states.configs),
        ),
        (
            not ctx.invoked_subcommand,
            lambda: ui.console.print(
                *(
                    f"[reset]{line[:25]}[colour.primary]{line[25:]}[/colour.primary]"
                    for line in (
                        importlib.resources.files("ryukit")
                        / "assets"
                        / "art"
                        / "logo.txt"
                    )
                    .read_text()
                    .splitlines()
                ),
                f"\nVERSION {importlib.metadata.version("ryukit")}",
                sep="\n",
                end="\n\n",
                new_line_start=True,
            ),
        ),
    ]:
        if not do:
            continue

        command()

        raise typer.Exit()

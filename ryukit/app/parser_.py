import importlib
import importlib.metadata
import importlib.resources
import json
import sqlite3
import typing

import jsonschema
import typer

from ..core import db, fs, state, ui
from ..helpers import typer_builder

__all__ = ["typer_builder_args"]


def command(
    ctx: typer.Context,
    show_configs: typing.Annotated[
        bool, typer.Option("--configs", help="Show configurations and exit.")
    ] = False,
):
    "A CLI tool for Ryujinx."

    fs.File.ROAMING_APP_DATA_DIR().mkdir(parents=True, exist_ok=True)

    if not fs.File.STATE_FILE().exists():
        fs.File.STATE_FILE().write_bytes(
            importlib.resources.read_binary("ryukit", "assets", "state.json")
        )

    if not fs.File.CONFIG_FILE().exists():
        with fs.File.CONFIG_FILE().open("w") as buffer:
            json.dump(
                {
                    k: v
                    for k, v in json.loads(
                        importlib.resources.read_text(
                            "ryukit",
                            "assets",
                            "configs",
                            "default-app-configs.json",
                            encoding="utf-8",
                        )
                    ).items()
                    if k != "$schema"
                },
                fp=buffer,
            )

    state.states.configs = json.loads(fs.File.CONFIG_FILE().read_bytes())

    for do, command in [
        (
            show_configs,
            lambda: ui.console.print_json(data=state.states.configs),
        ),
        (
            not ctx.invoked_subcommand,
            lambda: ui.console.print(
                *(
                    f"[reset]{line[:25]}[colour.primary]{line[25:]}[/colour.primary]"
                    for line in importlib.resources.read_text(
                        "ryukit", "assets", "logo.txt", encoding="utf-8"
                    ).splitlines()
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

    for *key, default in map(
        lambda args: map(str, args),
        [
            (
                "ryujinxConfigs",
                "distDir",
                fs.File.LOCAL_DATA_DIR()
                / typing.cast(
                    str,
                    typing.cast(
                        dict[str, object],
                        state.internal_configs["ryujinxInstall"],
                    )["defaultDistDirSuffix"],
                ),
            ),
            (
                "ryujinxConfigs",
                "roamingDataDir",
                fs.File.ROAMING_DATA_DIR()
                / typing.cast(
                    str,
                    typing.cast(
                        dict[str, object],
                        state.internal_configs["ryujinxInstall"],
                    )["defaultRoamingDirSuffix"],
                ),
            ),
        ],
    ):
        setting: dict[str, object] = state.states.configs
        *prefix, suffix = key

        for part in prefix:
            setting = typing.cast(typing.Any, setting[part])

        setting[suffix] = setting.get(suffix) or default

    try:
        typing.cast(
            typing.Any,
            jsonschema.Draft7Validator(
                json.loads(
                    importlib.resources.read_text(
                        "ryukit",
                        "assets",
                        "schemas",
                        "app-configs.schema.json",
                        encoding="utf-8",
                    )
                )
            ),
        ).validate(state.states.configs)

    except jsonschema.ValidationError as e:
        ui.console.print(
            f"[error]Malformed configuration file: {e.message}. This error came from {e.json_path}."
        )

        raise typer.Exit(1)

    with db.theme_applier(sqlite3.connect)("DATABASE") as conn:
        conn.executescript(
            importlib.resources.read_text(
                "ryukit", "assets", "setup_database.sql", encoding="utf-8"
            )
        )


typer_builder_args: typer_builder.TyperBuilderArgs = {
    "command": command,
    "typer_args": [{"invoke_without_command": True}],
}

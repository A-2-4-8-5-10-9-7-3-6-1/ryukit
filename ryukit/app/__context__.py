import importlib
import importlib.metadata
import importlib.resources
import json
import typing

import jsonschema
import typer

from ..core import db, ui
from ..core.fs import File
from ..core.ui import console
from ..utils import orchestration

__all__ = ["start", "configs", "system", "intersession_state", "app"]
app = ui.tuned(typer.Typer)(name="ryukit")
start = orchestration.and_packup(app)
configs: dict[str, object] = {}
system: dict[str, object] = {}
intersession_state: dict[str, object] = {}


@app.callback(no_args_is_help=True, invoke_without_command=True)
def _(
    version: typing.Annotated[
        bool, typer.Option("--version", help="Show version and exit.")
    ] = False,
):
    "A CLI tool for Ryujinx."

    configs.update(
        json.loads(
            File.CONFIG_FILE().read_bytes()
            if File.CONFIG_FILE().exists()
            else importlib.resources.read_binary(
                "ryukit.assets.configs", "default-app-configs.json"
            )
        )
    )
    system.update(
        json.loads(
            importlib.resources.read_text(
                "ryukit.assets.configs", "internal-configs.json"
            )
        )
    )
    configs.pop("$schema", None)
    try:
        typing.cast(
            typing.Any,
            jsonschema.Draft7Validator(
                json.loads(
                    importlib.resources.read_text(
                        "ryukit.assets", "app-configs.schema.json"
                    )
                )
            ),
        ).validate(configs)
    except jsonschema.ValidationError as e:
        console.print(
            f"[error]Malformed configuration file. {e.message}.",
            f"└── [italic]Error originated from {e.json_path}.",
            sep="\n",
        )
        raise typer.Exit(1)
    for *key, default in map(
        lambda args: map(str, args),
        [
            (
                "ryujinxConfigs",
                "distDir",
                File.LOCAL_DATA_DIR()
                / typing.cast(
                    str,
                    typing.cast(dict[str, object], system["ryujinxInstall"])[
                        "defaultDistDirSuffix"
                    ],
                ),
            ),
            (
                "ryujinxConfigs",
                "roamingDataDir",
                File.ROAMING_DATA_DIR()
                / typing.cast(
                    str,
                    typing.cast(dict[str, object], system["ryujinxInstall"])[
                        "defaultRoamingDirSuffix"
                    ],
                ),
            ),
        ],
    ):
        setting: dict[str, object] = configs
        *prefix, suffix = key
        for part in prefix:
            setting = typing.cast(dict[str, object], setting[part])
        setting[suffix] = setting.get(suffix) or default
    File.ROAMING_APP_DATA_DIR().mkdir(parents=True, exist_ok=True)
    intersession_state.update(
        json.loads(
            File.STATE_FILE().read_bytes()
            if File.STATE_FILE().exists()
            else importlib.resources.read_binary(
                "ryukit.assets.configs", "initial-state.json"
            )
        )
    )
    with db.connect() as conn:
        conn.executescript(
            importlib.resources.read_text(
                "ryukit.assets", "setup_database.sql"
            )
        )
    for do, command in [
        (
            version,
            lambda: console.print(
                f"RyuKit version {importlib.metadata.version("ryukit")}"
            ),
        )
    ]:
        if not do:
            continue
        command()
        raise typer.Exit()


@orchestration.packup_callback
def _():
    any(
        (
            file.parent.mkdir(parents=True, exist_ok=True),
            file.write_text(json.dumps(options, indent=2)),
        )
        for file, options in [
            (File.CONFIG_FILE(), configs),
            (File.STATE_FILE(), intersession_state),
        ]
        if options
    )

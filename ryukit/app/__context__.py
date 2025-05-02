import importlib
import importlib.metadata
import importlib.resources
import json
import pathlib
import typing

import jsonschema
import rich
import rich.theme
import typer

from ..core import db
from ..core.fs import File

__all__ = [
    "USER_CONFIGS",
    "INTERNAL_CONFIGS",
    "intersession_state",
    "command",
    "app",
    "console",
]
app = typer.Typer(name="ryukit", rich_markup_mode=None)
USER_CONFIGS: dict[str, object] = json.loads(
    pathlib.Path(File.CONFIG_FILE).read_bytes()
    if pathlib.Path(File.CONFIG_FILE).exists()
    else importlib.resources.read_binary(
        "ryukit.assets", "ryukitconfigs.default.json"
    )
)
command = app.command
console = rich.console.Console(
    theme=rich.theme.Theme({"error": "red"}), highlight=False
)


class IntersessionState(typing.TypedDict):
    ryujinx_meta: dict[str, object]


intersession_state: IntersessionState = {"ryujinx_meta": {}}


class InternalConfigsSpace:
    RyujinxInstallPaths = typing.TypedDict(
        "", {"dist": str, "registered": str, "keys": str}
    )
    RyujinxInstall = typing.TypedDict(
        "", {"sha256": str, "paths": RyujinxInstallPaths}
    )
    SaveBuckets = typing.TypedDict("", {"flow": dict[File, str]})
    InternalConfigs = typing.TypedDict(
        "", {"ryujinx_install": RyujinxInstall, "save_buckets": SaveBuckets}
    )


INTERNAL_CONFIGS: InternalConfigsSpace.InternalConfigs = {
    "ryujinx_install": {
        "sha256": "3e841a946595abc56c02409e165c62cb8e049963b54853dc551b2918e1f25d17",
        "paths": {
            "dist": File.RYUJINX_DIST_DIR,
            "registered": f"{File.RYUJINX_DATA_DIR.value}/bis/system/Contents/registered",
            "keys": f"{File.RYUJINX_DATA_DIR.value}/system",
        },
    },
    "save_buckets": {
        "flow": {
            File.SAVE_INSTANCE_META: f"{File.RYUJINX_DATA_DIR.value}/bis/user/saveMeta",
            File.SAVE_INSTANCE_USER_DATA: f"{File.RYUJINX_DATA_DIR.value}/bis/user/save",
            File.SAVE_INSTACE_SYSTEM_DATA: f"{File.RYUJINX_DATA_DIR.value}/bis/system/save",
        }
    },
}


@app.callback(no_args_is_help=True, invoke_without_command=True)
def _(
    version: typing.Annotated[
        bool, typer.Option("--version", help="Show version and exit.")
    ] = False,
):
    "A CLI tool for Ryujinx."

    try:
        typing.cast(
            typing.Any,
            jsonschema.Draft7Validator(
                json.loads(
                    importlib.resources.read_text(
                        "ryukit.assets", "ryukitconfigs.schema.json"
                    )
                )
            ),
        ).validate(USER_CONFIGS)
    except jsonschema.ValidationError as e:
        console.print(
            f"[error]Malformed configuration file. {e.message}.",
            f"└── Error originated from {e.json_path}.",
            sep="\n",
        )
        raise typer.Exit(1)
    pathlib.Path(File.ROAMING_DATA).mkdir(parents=True, exist_ok=True)
    intersession_state.update(
        json.loads(pathlib.Path(File.STATE_FILE).read_bytes())
        if pathlib.Path(File.STATE_FILE).exists()
        else {}
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

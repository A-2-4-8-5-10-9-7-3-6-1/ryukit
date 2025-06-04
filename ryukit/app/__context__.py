import contextlib
import importlib
import importlib.metadata
import importlib.resources
import json
import pathlib
from collections.abc import Callable
from typing import Annotated, Any, Literal, TypedDict, cast

import click
import jsonschema
import rich
import typer

from .. import utils
from ..libs import db, paths

__all__ = [
    "USER_CONFIGS",
    "INTERNAL_CONFIGS",
    "command",
    "app",
    "console",
    "PARSERS",
]
app = typer.Typer(rich_markup_mode="rich")
command = app.command
console = rich.console.Console(highlight=False)
USER_CONFIGS: dict[str, Any] = (
    json.loads(pathlib.Path(paths.CONFIG_FILE).read_bytes())
    if pathlib.Path(paths.CONFIG_FILE).exists()
    else {
        "$schema": "https://github.com/A-2-4-8-5-10-9-7-3-6-1/ryukit/tree/main/ryukit/ryukitconfigs.schema.json",
        "ryujinxInstallURL": None,
    }
)
PARSERS: dict[str, Callable[..., Any]] = {}
CALLBACKS: dict[str, Callable[..., Any]] = {}


@utils.use
def INTERNAL_CONFIGS():
    RyujinxInstall = TypedDict(
        "",
        {
            "sha256": str,
            "paths": dict[Literal["dist", "registered", "keys"], str],
        },
    )
    SaveBuckets = TypedDict("", {"flow": dict[str, str]})
    InternalConfigs = TypedDict(
        "", {"ryujinx_install": RyujinxInstall, "save_buckets": SaveBuckets}
    )
    return cast(
        InternalConfigs,
        {
            "ryujinx_install": {
                "sha256": "3e841a946595abc56c02409e165c62cb8e049963b54853dc551b2918e1f25d17",
                "paths": {
                    "dist": paths.RYUJINX_DIST_DIR,
                    "registered": f"{paths.RYUJINX_DATA_DIR}/bis/system/Contents/registered",
                    "keys": f"{paths.RYUJINX_DATA_DIR}/system",
                },
            },
            "save_buckets": {
                "flow": {
                    paths.SAVE_INSTANCE_META: f"{paths.RYUJINX_DATA_DIR}/bis/user/saveMeta",
                    paths.SAVE_INSTANCE_USER_DATA: f"{paths.RYUJINX_DATA_DIR}/bis/user/save",
                    paths.SAVE_INSTANCE_SYSTEM_DATA: f"{paths.RYUJINX_DATA_DIR}/bis/system/save",
                }
            },
        },
    )


@utils.PATTERNS["dict_decorator"](PARSERS, key="bucket")
@contextlib.contextmanager
def _(id_: int, /):
    with db.client() as client:
        save = client.get(db.RyujinxSave, id_)
        if not save:
            raise typer.BadParameter("Unrecognized bucket ID.")
        yield client, save


@utils.PATTERNS["dict_decorator"](CALLBACKS, key="version")
@utils.PATTERNS["run_one"]("/")
@utils.PATTERNS["flag_callback"]
def _():
    console.print(f"RyuKit version {importlib.metadata.version("ryukit")}")


@app.callback()
@utils.PATTERNS["run_one"]("/")
def _(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show version and exit.",
            callback=CALLBACKS["version"],
        ),
    ] = False,
):
    "A CLI tool for Ryujinx."

    try:
        cast(
            Any,
            jsonschema.Draft7Validator(
                json.loads(
                    importlib.resources.read_text(
                        "ryukit", "ryukitconfigs.schema.json"
                    )
                )
            ),
        ).validate(USER_CONFIGS)
    except jsonschema.ValidationError as e:
        raise click.UsageError(
            f"Malformed configuration file, '{e.message}'.\n"
            f"└── Origin: '{e.json_path}'."
        )
    any(
        pathlib.Path(path).parent.mkdir(exist_ok=True, parents=True)
        for path in [paths.TRACKER_FILE, paths.DATABASE_FILE]
    )

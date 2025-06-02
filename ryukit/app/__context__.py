import contextlib
import importlib
import importlib.metadata
import importlib.resources
import json
import pathlib
from typing import Annotated, Any, Literal, TypedDict, cast

import jsonschema
import rich
import rich.theme
import typer

from .. import utils
from ..libs import db, paths

__all__ = [
    "USER_CONFIGS",
    "INTERNAL_CONFIGS",
    "command",
    "app",
    "console",
    "bucket",
]
app = typer.Typer(rich_markup_mode="rich")
USER_CONFIGS: dict[str, Any] = (
    json.loads(pathlib.Path(paths.CONFIG_FILE).read_bytes())
    if pathlib.Path(paths.CONFIG_FILE).exists()
    else {
        "$schema": "https://github.com/A-2-4-8-5-10-9-7-3-6-1/ryukit/tree/main/ryukit/ryukitconfigs.schema.json",
        "ryujinxInstallURL": None,
    }
)
command = app.command
console = rich.console.Console(
    theme=rich.theme.Theme({"error": "red"}), highlight=False
)


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


@contextlib.contextmanager
def bucket(id_: int, /):
    """
    Get a save bucket from an ID.

    :param id_: The bucket's ID.
    :raises typer.Exit: If the bucket doesn't exist.
    """

    with db.client() as client:
        save = client.get(db.RyujinxSave, {"id": id_})
        if not save:
            console.print(f"[error]No bucket with ID '{id_}'.")
            raise typer.Exit(1)
        yield client, save


@app.callback(no_args_is_help=True, invoke_without_command=True)
def _(
    version: Annotated[
        bool, typer.Option("--version", help="Show version and exit.")
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
        console.print(
            f"[error]Malformed configuration file. {e.message}.",
            f"└── Error originated from {e.json_path}.",
            sep="\n",
        )
        raise typer.Exit(1)
    pathlib.Path(paths.DATABASE_FILE).parent.mkdir(exist_ok=True, parents=True)
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

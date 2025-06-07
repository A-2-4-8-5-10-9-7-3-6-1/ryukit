import contextlib
import importlib
import importlib.metadata
import pathlib
from typing import Annotated, Any, Literal, TypedDict, cast

import click
import rich
import rich.theme
import typer

from ..libs import db, paths, typer_extensions
from ..utils import patterns

__all__ = ["SYSTEM_CONFIGS", "command", "app", "PARSERS"]
app = typer.Typer(rich_markup_mode="rich")
command = app.command
PARSERS: dict[str, Callable[..., Any]] = {}
CALLBACKS: dict[str, Callable[..., Any]] = {}


@patterns.use
def SYSTEM_CONFIGS():
    RyujinxInstall = TypedDict(
        "",
        {
            "sha256": str,
            "paths": dict[Literal["dist", "registered", "keys"], str],
        },
    )
    SaveBuckets = TypedDict("", {"flow": dict[str, str]})
    SystemConfigs = TypedDict(
        "", {"ryujinx_install": RyujinxInstall, "save_buckets": SaveBuckets}
    )
    return cast(
        SystemConfigs,
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


@patterns.dict_decorator(PARSERS, key="bucket")
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
            raise click.BadParameter("Unrecognized bucket ID.")
        yield client, save


@patterns.dict_decorator(CALLBACKS, key="version")
@patterns.on_request
@typer_extensions.then_terminate
def _():
    rich.print(f"RyuKit version {importlib.metadata.version("ryukit")}")


@app.callback()
def _(
    version: Annotated[
        bool, typer.Option("--version", help="Show version and exit.")
    ] = False,
):
    "A CLI tool for Ryujinx."

    any(
        pathlib.Path(path).parent.mkdir(exist_ok=True, parents=True)
        for path in [paths.TRACKER_FILE, paths.DATABASE_FILE]
    )

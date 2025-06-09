import contextlib
import functools
import importlib
import importlib.metadata
import pathlib
import shutil
from collections.abc import Callable, Sequence
from typing import Annotated, Any, Literal, TypedDict, cast

import click
import rich
import typer

from ..libs import db, paths
from ..utils import qol

__all__ = [
    "SYSTEM_CONFIGS",
    "command",
    "app",
    "PARSERS",
    "on_request",
    "channel_save_bucket",
]
app = typer.Typer(rich_markup_mode="rich")
command = app.command
PARSERS: dict[str, Callable[..., Any]] = {}
started = False


@qol.use
def _():
    initial = typer.Typer.__call__

    @functools.wraps(initial)
    def inner(*args: ..., **kwargs: ...):
        global started
        started = True
        return initial(*args, **kwargs)

    typer.Typer.__call__ = inner


def channel_save_bucket(id_: int, /, upstream: bool):
    """
    Copy save content between a save bucket and Ryujinx.

    :param id_: The save bucket's ID.
    :param upstream: Copy from save bucket into Ryujinx?
    """

    def rotate[T](values: Sequence[T]):
        return (iter if upstream else reversed)(values)

    for source, dest in map(
        rotate,
        map(
            tuple,
            map(
                lambda p: map(pathlib.Path, p),
                (
                    (x.format(id=id_), y)
                    for x, y in SYSTEM_CONFIGS["save_buckets"]["flow"].items()
                ),
            ),
        ),
    ):
        if dest.exists():
            shutil.rmtree(dest)
        if not source.exists():
            continue
        shutil.copytree(source, dest)


def on_request(func: Callable[[], None], /):
    """Trigger a function on request."""

    def inner(do: bool = True):
        func() if do else None

    return inner


def then_terminate[**P](func: Callable[P, None], /):
    """Force termination, via an exception, after execution of subsequent function."""

    @functools.wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs):
        func(*args, **kwargs)
        if started:
            raise click.exceptions.Exit()

    return inner


@qol.use
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


@qol.in_dict(PARSERS, key="bucket")
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


@app.callback()
def _(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show version and exit.",
            callback=on_request(
                then_terminate(
                    lambda: rich.print(
                        f"RyuKit version {importlib.metadata.version("ryukit")}"
                    )
                )
            ),
        ),
    ] = False,
):
    "A CLI tool for Ryujinx."

    any(
        pathlib.Path(path).parent.mkdir(exist_ok=True, parents=True)
        for path in [paths.TRACKER_FILE, paths.DATABASE_FILE]
    )

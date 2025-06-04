import importlib
import importlib.resources
import json
import pathlib
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from typing import Annotated, Literal, TypedDict, cast

import click
import psutil
import typer

from .. import utils
from ..libs import components, paths
from .__context__ import command, console

__all__ = ["track", "Tracker", "FREQUENCIES", "CALLBACKS"]
FREQUENCIES = {"process_checking": 0.3, "tracker_logging": 0.1}
CALLBACKS: dict[Literal["halt", "status"], Callable[..., None]] = {}


class Tracker(TypedDict):
    pid: int | None
    runtime: float | None
    diff: int | None
    bucket: int | None


TRACKER_CONTAINER: list[Tracker] = []


def load_tracker():
    TRACKER_CONTAINER.clear()
    (
        TRACKER_CONTAINER.append(
            json.loads(pathlib.Path(paths.TRACKER_FILE).read_bytes())
        )
        if pathlib.Path(paths.TRACKER_FILE).exists()
        else None
    )


def tracker_active():
    return (
        TRACKER_CONTAINER
        and TRACKER_CONTAINER[0]["pid"] is not None
        and psutil.pid_exists(TRACKER_CONTAINER[0]["pid"])
        and psutil.Process(TRACKER_CONTAINER[0]["pid"]).status()
        != psutil.STATUS_ZOMBIE
    )


@utils.PATTERNS["dict_decorator"](CALLBACKS, key="halt")
@utils.PATTERNS["run_one"]("/track")
@utils.PATTERNS["flag_callback"]
def _():
    if not tracker_active():
        raise click.UsageError("Tracker is not active.")
    psutil.Process(cast(int, TRACKER_CONTAINER[0]["pid"])).send_signal(
        signal.SIGINT
    )
    with components.Status("Deactivating tracker...", spinner="dots2"):
        while tracker_active():
            time.sleep(FREQUENCIES["process_checking"])
            load_tracker()


@utils.PATTERNS["dict_decorator"](CALLBACKS, key="status")
@utils.PATTERNS["run_one"]("/track")
@utils.PATTERNS["flag_callback"]
def _():
    with components.Live(console=console) as live:
        while True:
            live.update(
                "[reset]\n".join(
                    [
                        f". Writing to bucket with ID: {cast(int, TRACKER_CONTAINER[0]['bucket'])}",
                        f". Diff: {'[green]-' if cast(int, TRACKER_CONTAINER[0]['diff']) < 0 else '[blue]+'}{abs(utils.megabytes(cast(int, TRACKER_CONTAINER[0]["diff"]))):.1f}MB",
                        f". Lifetime: {cast(float, TRACKER_CONTAINER[0]["runtime"]) / 60:.2f} minute(s)",
                        f". State: [green bold]ACTIVE",
                    ]
                    if tracker_active()
                    else [
                        ". Writing to bucket with ID: Unavailable",
                        ". Diff: Unavailable",
                        ". Lifetime: Unavailable",
                        ". State: [yellow bold]RESTING",
                    ]
                )
            )
            time.sleep(FREQUENCIES["tracker_logging"])
            try:  # risk of reloading whilst background process is writing.
                load_tracker()
            except json.decoder.JSONDecodeError:
                pass


@command("track")
@utils.PATTERNS["run_one"]("/track")
def track(
    use_bucket: Annotated[
        int,
        typer.Argument(
            help="The save bucket to track into.", show_default=False
        ),
    ],
    status: Annotated[
        bool,
        typer.Option(
            "--status",
            help="Show tracking status and exit.",
            show_default=False,
            callback=CALLBACKS["status"],
        ),
    ] = False,
    halt: Annotated[
        bool,
        typer.Option(
            "--halt",
            help="Reset the tracker.",
            show_default=False,
            callback=CALLBACKS["halt"],
        ),
    ] = False,
):
    """
    Monitor a Ryujinx play session and save changes into a bucket.

    NOTE: The tracker will stop immediately if there's no active Ryujinx process.
    NOTE: A non-existent bucket ID will be created anew.
    WARNING: The tracker is sure to invoke the save-pull command once awakened, this will overwrite any previous data.
    """

    if use_bucket < 0:
        raise typer.BadParameter("Must be non-negative integer.")
    load_tracker()
    if tracker_active():
        raise typer.BadParameter("Tracker is already running.")
    pathlib.Path(paths.TRACKER_FILE).write_text(
        utils.json_dumps(
            {"bucket": use_bucket, "runtime": None, "diff": None, "pid": None}
        )
    )
    load_tracker()
    subprocess.Popen(
        [
            sys.executable,
            str(importlib.resources.files("ryukit.app") / "__tracker__.py"),
        ],
        start_new_session=True,
    )
    with components.Status("Waking tracker...", spinner="dots2"):
        while TRACKER_CONTAINER[0]["runtime"] is None:
            time.sleep(FREQUENCIES["process_checking"])
            load_tracker()
    console.print(
        "Tracker activated.",
        "└── Use the '--status' option to monitor the tracker.",
        sep="\n",
    )

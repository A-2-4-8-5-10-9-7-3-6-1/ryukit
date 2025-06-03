import importlib
import importlib.resources
import json
import pathlib
import subprocess
import sys
import time
from typing import Annotated, TypedDict, cast

import psutil
import typer

from .. import utils
from ..libs import components, paths
from .__context__ import bucket, command, console
from .save.pull import pull

__all__ = ["track", "Tracker", "TRACK_FREQUENCY"]

TRACK_FREQUENCY = 0.2


class Tracker(TypedDict):
    pid: int
    runtime: float
    saveDiff: int
    bucket: int


@command("track")
def track(
    into: Annotated[
        int | None,
        typer.Argument(
            help="The save bucket to track into.", show_default=False
        ),
    ] = None,
    status: Annotated[
        bool,
        typer.Option(
            "--status",
            help="Show tracking status and exit.",
            show_default=False,
        ),
    ] = False,
    reset: Annotated[
        bool,
        typer.Option("--reset", help="Reset the tracker.", show_default=False),
    ] = False,
):
    """
    Monitor a Ryujinx play session and save changes into a bucket.

    WARNING: On success, this will surely invoke the save-pull command on whichever bucket 'into' points to.
    """

    def load_tracker():
        tracker_container.clear()
        tracker_container.append(
            json.loads(pathlib.Path(paths.TRACKER_FILE).read_bytes())
        )

    def tracker_active():
        pid = [*tracker_container, {"pid": -1}][0]["pid"]
        return (
            psutil.pid_exists(pid)
            and psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
        )

    if not any([into is not None, status, reset]):
        console.print("[error]Missing argument for INTO.")
        raise typer.Exit()
    tracker_container: list[Tracker] = []
    if pathlib.Path(paths.TRACKER_FILE).exists():
        load_tracker()
    if not tracker_active() and reset:
        console.print("[error]Tracker is inactive.")
        raise typer.Exit(1)
    if tracker_active() and into is not None:
        console.print("[error]Tracker is already active.")
        raise typer.Exit(1)
    if reset:
        psutil.Process(tracker_container[0]["pid"]).terminate()
        with utils.capture_out():
            pull(tracker_container[0]["bucket"])
        return console.print(
            f"Changes written to save bucket '{tracker_container[0]['bucket']}'."
        )
    if status:
        display = "\n".join(
            [
                ". Writing to bucket with ID: {bucket}",
                ". Save diff: {sign}{saveDiff}MB[/]",
                ". Lifetime: {lifetime:.2f}-minute",
                ". State: {state}",
            ]
        )
        with components.Live(console=console) as live:
            while True:
                live.update(
                    display.format(
                        **tracker_container[0],
                        lifetime=tracker_container[0]["runtime"] / 60,
                        state="ACTIVE" if tracker_active() else "DORMANT",
                        sign=(
                            "[none]"
                            if not tracker_container[0]["saveDiff"]
                            else (
                                "[green]+"
                                if tracker_container[0]["saveDiff"] < 0
                                else "[red]-"
                            )
                        ),
                    )
                )
                time.sleep(TRACK_FREQUENCY)
                previous = tracker_container[0]
                try:  # risk of reloading whilst background process is writing.
                    load_tracker()
                except json.decoder.JSONDecodeError:
                    tracker_container.append(previous)
    into = cast(int, into)
    with bucket(into) as (_, save):
        pathlib.Path(paths.TRACKER_FILE).write_text(
            utils.json_dumps(
                {
                    "bucket": into,
                    "runtime": 0,
                    "saveDiff": save.size,
                    "pid": -1,
                }
            )
        )
    subprocess.Popen(
        [
            sys.executable,
            str(importlib.resources.files("ryukit.app") / "__tracker__.py"),
            str(into),
        ],
        start_new_session=True,
    )
    console.print(
        "Tracker activated.",
        "└── Use the '--status' option to monitor the tracker.",
        sep="\n",
    )

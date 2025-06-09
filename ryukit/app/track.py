import json
import os
import pathlib
import signal
import subprocess
import time
from collections.abc import Callable
from typing import Annotated, Any, Iterator, TypedDict, cast

import psutil
import rich
import rich.live
import rich.status
import rich.tree
import sqlalchemy
import typer

from ..libs import db, paths
from ..utils import misc, qol
from .__context__ import SYSTEM_CONFIGS, command, on_request, then_terminate

__all__ = []
CALLBACKS: dict[str, Callable[..., None]] = {}
FREQUENCY = 0.3


class Tracker(TypedDict):
    pid: int | None
    runtime: float | None
    diff: int | None
    bucket: int | None


TRACKER_CONTAINER: list[Tracker] = []


def load_tracker():
    TRACKER_CONTAINER.clear()
    try:
        (
            TRACKER_CONTAINER.append(
                json.loads(pathlib.Path(paths.TRACKER_FILE).read_bytes())
            )
            if pathlib.Path(paths.TRACKER_FILE).exists()
            else None
        )
    except json.JSONDecodeError:  # Could attempt read before file is ready.
        pass
    return (
        TRACKER_CONTAINER != []
        and TRACKER_CONTAINER[0]["pid"] is not None
        and psutil.pid_exists(TRACKER_CONTAINER[0]["pid"])
        and psutil.Process(TRACKER_CONTAINER[0]["pid"]).status()
        != psutil.STATUS_ZOMBIE
    )


@qol.in_dict(CALLBACKS, key="start")
@on_request
@then_terminate
def _():
    load_tracker()
    TRACKER_CONTAINER[0]["bucket"] = cast(int, TRACKER_CONTAINER[0]["bucket"])
    TRACKER_CONTAINER[0]["pid"] = os.getpid()
    TRACKER_CONTAINER[0]["runtime"] = 0
    TRACKER_CONTAINER[0]["diff"] = 0
    initial_size = TRACKER_CONTAINER[0]["diff"]
    ryujinx_sessions: Iterator[psutil.Process] = iter([])
    start_time: float | None = None
    try:
        while start_time is None or any(ryujinx_sessions):
            for _ in ryujinx_sessions or []:
                raise RuntimeError("Multiple Ryujinx sessions running.")
            time.sleep(FREQUENCY)
            ryujinx_sessions = filter(
                lambda process: process.name() == "Ryujinx.exe"
                and process.status() != psutil.STATUS_ZOMBIE,
                psutil.process_iter(["name", "status"]),
            )
            TRACKER_CONTAINER[0]["runtime"] += (
                time.perf_counter() - start_time if start_time else 0
            )
            start_time = time.perf_counter()
            try:
                TRACKER_CONTAINER[0]["diff"] = (
                    sum(
                        misc.size(path, sizing="dir")
                        for path in SYSTEM_CONFIGS["save_buckets"][
                            "flow"
                        ].values()
                    )
                    - initial_size
                )
            except (
                FileNotFoundError
            ):  # Files may be deleted during calculation
                pass
            pathlib.Path(paths.TRACKER_FILE).write_text(
                misc.json_dumps(TRACKER_CONTAINER[0])
            )
    finally:
        with db.client() as client:
            if not client.get(db.RyujinxSave, TRACKER_CONTAINER[0]["bucket"]):
                subprocess.run(
                    ["ryukit", "save", "create"], capture_output=True
                )
                cast(
                    db.RyujinxSave,
                    client.scalar(
                        sqlalchemy.select(db.RyujinxSave)
                        .order_by(db.RyujinxSave.id.desc())
                        .limit(1)
                    ),
                ).id = TRACKER_CONTAINER[0]["bucket"]
            client.flush()
        subprocess.run(
            ["ryukit", "save", "pull", str(TRACKER_CONTAINER[0]["bucket"])],
            capture_output=True,
        )
        TRACKER_CONTAINER[0]["pid"] = None
        pathlib.Path(paths.TRACKER_FILE).write_text(
            misc.json_dumps(TRACKER_CONTAINER[0])
        )


@qol.in_dict(CALLBACKS, key="stop")
@on_request
@then_terminate
def _():
    if not load_tracker():
        raise click.UsageError("Tracker is not active.")
    psutil.Process(cast(int, TRACKER_CONTAINER[0]["pid"])).send_signal(
        signal.SIGINT
    )
    with rich.status.Status("Deactivating tracker..."):
        while load_tracker():
            time.sleep(FREQUENCY)


@qol.in_dict(CALLBACKS, key="status")
@on_request
@then_terminate
def _():
    container = cast(list[dict[str, Any]], TRACKER_CONTAINER)
    with rich.live.Live() as live:
        while True:
            live.update(
                "[bold]Writing into (bucket ID)[/]: {id}"
                "\n[reset][bold]Diff (MB)[/]:                {diff}"
                "\n[reset][bold]Lifetime (minutes)[/]:       {lifetime}"
                "\n[reset][bold]State[/]:                    {state}".format(
                    **(
                        {
                            "id": container[0]["bucket"],
                            "diff": f"{'[green]-' if container[0]['diff'] < 0 else '[blue]+'}{abs(misc.megabytes(container[0]["diff"])):.1f}",
                            "lifetime": f"{container[0]["runtime"] / 60:.2f}",
                            "state": "[green bold]ACTIVE",
                        }
                        if load_tracker()
                        else {
                            "id": "[dim]Unavailable",
                            "diff": "[dim]Unavailable",
                            "lifetime": "[dim]Unavailable",
                            "state": "[yellow bold]RESTING",
                        }
                    )
                )
            )
            time.sleep(FREQUENCY)


@command("track")
def _(
    use_bucket: Annotated[
        int,
        typer.Argument(
            help="The save bucket to track into.", show_default=False
        ),
    ],
    start: Annotated[
        bool,
        typer.Option(
            "--start",
            help="Do not use this option.",
            hidden=True,
            callback=CALLBACKS["start"],
        ),
    ] = False,
    status: Annotated[
        bool,
        typer.Option(
            "--status",
            help="Show tracking status.",
            show_default=False,
            callback=CALLBACKS["status"],
        ),
    ] = False,
    stop: Annotated[
        bool,
        typer.Option(
            "--stop",
            help="Stop the background tracker.",
            show_default=False,
            callback=CALLBACKS["stop"],
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
        raise click.BadParameter("Must be non-negative integer.")
    if load_tracker():
        raise click.ClickException("Tracker is already running.")
    pathlib.Path(paths.TRACKER_FILE).write_text(
        misc.json_dumps(
            {"bucket": use_bucket, "runtime": None, "diff": None, "pid": None}
        )
    )
    pid = subprocess.Popen(["ryukit", "track", "--start"]).pid
    with rich.status.Status("Waking tracker..."):
        while not load_tracker() or TRACKER_CONTAINER[0]["pid"] != pid:
            time.sleep(FREQUENCY)
    tree = rich.tree.Tree("Tracker activated")
    tree.add("Use the '--status' option to monitor the tracker.")
    rich.print(tree)

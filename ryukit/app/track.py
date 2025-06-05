import time
from collections.abc import Callable
from typing import Annotated, Any, TypedDict, cast

import psutil
import rich
import rich.live
import rich.status
import typer

from ..libs import paths, typer_extensions
from ..utils import misc, patterns
from .__context__ import command

__all__ = ["Tracker", "FREQUENCIES", "CALLBACKS"]
FREQUENCIES = {"process_checking": 0.3, "tracker_logging": 0.1}
CALLBACKS: dict[str, Callable[..., None]] = {}


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
    return (
        TRACKER_CONTAINER
        and TRACKER_CONTAINER[0]["pid"] is not None
        and psutil.pid_exists(TRACKER_CONTAINER[0]["pid"])
        and psutil.Process(TRACKER_CONTAINER[0]["pid"]).status()
        != psutil.STATUS_ZOMBIE
    )


@patterns.dict_decorator(CALLBACKS, key="halt")
@patterns.on_request
@typer_extensions.then_terminate
def _():
    if not load_tracker():
        raise click.UsageError("Tracker is not active.")
    psutil.Process(cast(int, TRACKER_CONTAINER[0]["pid"])).send_signal(
        signal.SIGINT
    )
    with rich.status.Status("Deactivating tracker...", spinner="dots2"):
        while load_tracker():
            time.sleep(FREQUENCIES["process_checking"])


@patterns.dict_decorator(CALLBACKS, key="status")
@patterns.on_request
@typer_extensions.then_terminate
def _():
    container = cast(list[dict[str, Any]], TRACKER_CONTAINER)
    with rich.live.Live() as live:
        while True:
            live.update(
                ". [bold]Writing into (bucket ID)[/]: {id}"
                "\n[reset]. [bold]Diff (MB)[/]: {diff}"
                "\n[reset]. [bold]Lifetime (minutes)[/]: {lifetime}"
                "\n[reset]. [bold]State[/]: {state}".format(
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
            time.sleep(FREQUENCIES["tracker_logging"])


@command("track")
def _(
    use_bucket: Annotated[
        int,
        typer.Argument(
            help="The save bucket to track into.", show_default=False
        ),
    ],
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
        raise click.BadParameter("Tracker is already running.")
    pathlib.Path(paths.TRACKER_FILE).write_text(
        misc.json_dumps(
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
    with rich.status.Status("Waking tracker...", spinner="dots2"):
        while TRACKER_CONTAINER[0]["runtime"] is None:
            time.sleep(FREQUENCIES["process_checking"])
            load_tracker()
    rich.print(
        "Tracker activated.",
        "└── Use the '--status' option to monitor the tracker.",
        sep="\n",
    )

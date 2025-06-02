import datetime
import time
from typing import Annotated, cast

import psutil
import typer

from .. import utils
from ..libs import components
from .__context__ import INTERNAL_CONFIGS, bucket, command, console
from .save.pull import pull

__all__ = ["track"]


@command("track")
def track(
    into: Annotated[
        int,
        typer.Argument(
            help="The save bucket to track into.", show_default=False
        ),
    ],
):
    """
    Monitor a Ryujinx play session and save changes into a bucket.

    WARNING
    -------
    * This will surely invoke the save-pull command on whichever bucket 'into' points to.
    * Avoid running multiple Ryujinx processes when using this command.
    """

    try:
        process = next(
            filter(
                lambda process: process.name() == "Ryujinx.exe"
                and process.status() != psutil.STATUS_ZOMBIE,
                psutil.process_iter(["name", "pid", "create_time", "status"]),
            )
        )
    except:
        console.print(
            "[error]Couldn't find an active Ryujinx process.",
            "└── Is Ryujinx running?",
            sep="\n",
        )
        raise typer.Exit(1)
    with bucket(into) as (_, save):
        initials = {
            "time": datetime.datetime.fromtimestamp(process.create_time()),
            "size": save.size,
        }
    console.print(f"Monitoring Ryujinx through process '{process.pid}'.")
    status = "\n".join(
        [
            "",
            ". playtime: {playtime}",
            ". session diff: {sign}{session_diff:.1f}MB[/]",
            "",
        ]
    )
    try:
        with components.Live(console=console) as live:
            while (
                psutil.pid_exists(process.pid)
                and process.status() != psutil.STATUS_ZOMBIE
            ):
                size_diff = sum(
                    utils.size(path, sizing="dir")
                    for path in INTERNAL_CONFIGS["save_buckets"][
                        "flow"
                    ].values()
                ) - cast(int, initials["size"])
                live.update(
                    status.format(
                        playtime=str(
                            datetime.datetime.now()
                            - cast(datetime.datetime, initials["time"])
                        ).split(".")[0],
                        session_diff=utils.megabytes(size_diff),
                        sign="[green]" if size_diff < 0 else "[red]+",
                    )
                )
                time.sleep(0.2)
        console.print("Session terminated.")
    except KeyboardInterrupt:
        console.print("Tracking was forcefully stopped.")
    finally:
        console.print("Writing to bucket...")
        with utils.capture_out():
            pull(into)

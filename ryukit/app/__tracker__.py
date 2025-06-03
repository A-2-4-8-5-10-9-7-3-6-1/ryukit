# NOTE: This is a script, intended for use only through the track command.

import json
import os
import pathlib
import time
from collections.abc import Iterable

import psutil

from ryukit import utils
from ryukit.app.__context__ import INTERNAL_CONFIGS
from ryukit.app.save.pull import pull
from ryukit.app.track import TRACK_FREQUENCY
from ryukit.libs import paths

tracker = json.loads(pathlib.Path(paths.TRACKER_FILE).read_bytes())
initial_size = tracker["saveDiff"]
tracker["pid"] = os.getpid()
ryujinx_sessions: Iterable[psutil.Process] | None = None
try:
    while ryujinx_sessions is None or any(ryujinx_sessions):
        for _ in ryujinx_sessions or []:
            raise Exception("[error]Multiple sessions are running.")
        time.sleep(TRACK_FREQUENCY)
        ryujinx_sessions = filter(
            lambda process: process.name() == "Ryujinx.exe"
            and process.status() != psutil.STATUS_ZOMBIE,
            psutil.process_iter(["name", "status"]),
        )
        tracker["runtime"] += TRACK_FREQUENCY
        try:
            tracker["save_diff"] = (
                sum(
                    utils.size(path, sizing="dir")
                    for path in INTERNAL_CONFIGS["save_buckets"][
                        "flow"
                    ].values()
                )
                - initial_size
            )
        except FileNotFoundError:  # Files may be deleted during calculation
            pass
        pathlib.Path(paths.TRACKER_FILE).write_text(utils.json_dumps(tracker))
finally:
    with utils.capture_out():
        pull(tracker["bucket"])

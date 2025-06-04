# This is a script, intended for use only through the track command.

import json
import os
import pathlib
import time
from collections.abc import Iterable
from typing import cast

import psutil
import sqlalchemy

from ryukit import utils
from ryukit.app.__context__ import INTERNAL_CONFIGS, PARSERS
from ryukit.app.save.create import create
from ryukit.app.save.pull import pull
from ryukit.app.track import FREQUENCIES, Tracker
from ryukit.libs import db, paths

tracker: Tracker = json.loads(pathlib.Path(paths.TRACKER_FILE).read_bytes())
tracker["bucket"] = cast(int, tracker["bucket"])
tracker["pid"] = os.getpid()
tracker["runtime"] = 0
tracker["diff"] = 0
initial_size = tracker["diff"]
ryujinx_sessions: Iterable[psutil.Process] | None = None
try:
    while ryujinx_sessions is None or any(ryujinx_sessions):
        for _ in ryujinx_sessions or []:
            raise RuntimeError("Multiple Ryujinx sessions running.")
        time.sleep(FREQUENCIES["tracker_logging"])
        ryujinx_sessions = filter(
            lambda process: process.name() == "Ryujinx.exe"
            and process.status() != psutil.STATUS_ZOMBIE,
            psutil.process_iter(["name", "status"]),
        )
        tracker["runtime"] += FREQUENCIES["tracker_logging"]
        try:
            tracker["diff"] = (
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
    with db.client() as client:
        if not client.get(db.RyujinxSave, tracker["bucket"]):
            with utils.capture_out():
                create()
            cast(
                db.RyujinxSave,
                client.scalar(
                    sqlalchemy.select(db.RyujinxSave)
                    .order_by(db.RyujinxSave.id.desc())
                    .limit(1)
                ),
            ).id = tracker["bucket"]
        client.flush()
    with utils.capture_out():
        pull(PARSERS["bucket"](tracker["bucket"]))
    tracker["pid"] = None
    pathlib.Path(paths.TRACKER_FILE).write_text(utils.json_dumps(tracker))

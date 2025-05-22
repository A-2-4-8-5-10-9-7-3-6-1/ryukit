"""App implementation."""

import importlib
import importlib.resources
import json
import pathlib
import runpy

from ..libs import paths
from .__context__ import INTERSESSION_STATE, USER_CONFIGS, app

__all__ = ["start"]
any(
    map(
        lambda _: False,
        map(
            runpy.run_path,
            map(
                str,
                (
                    importlib.resources.files("ryukit.app") / file
                    for file in [
                        "install_ryujinx.py",
                        "save/apply.py",
                        "save/create.py",
                        "save/drop.py",
                        "save/dump.py",
                        "save/ls.py",
                        "save/pull.py",
                        "save/relabel.py",
                        "save/restore.py",
                    ]
                ),
            ),
        ),
    )
)


def start():
    try:
        app()
    finally:
        USER_CONFIGS["$schema"] = (
            "https://github.com/A-2-4-8-5-10-9-7-3-6-1/ryukit/blob/dev/ryukit/ryukitconfigs.json"
        )
        any(
            map(
                lambda _: False,
                (
                    (
                        pathlib.Path(file).parent.mkdir(
                            parents=True, exist_ok=True
                        ),
                        pathlib.Path(file).write_text(
                            json.dumps(options, indent=2)
                        ),
                    )
                    for file, options in [
                        (paths.CONFIG_FILE, USER_CONFIGS),
                        (paths.STATE_FILE, INTERSESSION_STATE),
                    ]
                    if options
                ),
            )
        )

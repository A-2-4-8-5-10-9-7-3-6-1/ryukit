"""App implementation."""

import copy
import importlib
import importlib.resources
import json
import pathlib
import runpy

from ..core.fs import File
from .__context__ import USER_CONFIGS, app, intersession_state

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
        user_configs = copy.copy(USER_CONFIGS)
        user_configs.pop("$schema", None)
        any(
            (
                pathlib.Path(file).parent.mkdir(parents=True, exist_ok=True),
                pathlib.Path(file).write_text(json.dumps(options, indent=2)),
            )
            for file, options in [
                (File.CONFIG_FILE, user_configs),
                (File.STATE_FILE, intersession_state),
            ]
            if options
        )

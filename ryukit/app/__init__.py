"""App implementation."""

import pathlib
import runpy

from .. import utils
from ..libs import paths
from .__context__ import INTERSESSION_STATE, USER_CONFIGS, app

__all__ = ["start"]
any(
    map(
        lambda _: False,
        map(
            runpy.run_module,
            [
                "ryukit.app.install_ryujinx",
                "ryukit.app.save.apply",
                "ryukit.app.save.create",
                "ryukit.app.save.drop",
                "ryukit.app.save.dump",
                "ryukit.app.save.ls",
                "ryukit.app.save.pull",
                "ryukit.app.save.relabel",
                "ryukit.app.save.restore",
            ],
        ),
    )
)


def start():
    try:
        app()
    finally:
        any(
            map(
                lambda _: False,
                (
                    (
                        pathlib.Path(file).parent.mkdir(
                            parents=True, exist_ok=True
                        ),
                        pathlib.Path(file).write_text(
                            utils.json_dumps(options, indent=2)
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

"""App implementation."""

import pathlib
import runpy

from .. import utils
from ..libs import paths
from .__context__ import USER_CONFIGS, app

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
                "ryukit.app.track",
            ],
        ),
    )
)


def start():
    try:
        app()
    finally:
        pathlib.Path(paths.CONFIG_FILE).parent.mkdir(
            parents=True, exist_ok=True
        )
        pathlib.Path(paths.CONFIG_FILE).write_text(
            utils.json_dumps(USER_CONFIGS, indent=2)
        )

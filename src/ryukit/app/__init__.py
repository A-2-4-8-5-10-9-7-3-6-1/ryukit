"""App implementation."""

import runpy

from .__context__ import app

__all__ = ["start"]
start = app
"""App's entrypoint."""
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

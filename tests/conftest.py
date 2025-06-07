import importlib
import importlib.resources
import io
import pathlib
import shutil
import sys
from typing import cast

from pytest import fixture

from ryukit.libs import paths

__all__ = ["seed"]
cast(io.TextIOWrapper, sys.stdout).reconfigure(errors="ignore")


@fixture
def seed():
    any(
        shutil.rmtree(path, ignore_errors=True) and False
        for path in (
            pathlib.Path(paths.DATABASE_FILE).parent,
            pathlib.Path(paths.TRACKER_FILE).parent,
            paths.RYUJINX_DIST_DIR,
            paths.RYUJINX_DATA_DIR,
        )
    )
    any(
        (
            pathlib.Path(path).mkdir(parents=True, exist_ok=True),
            shutil.copy(
                str(importlib.resources.files("tests") / "data"), path
            ),
        )
        and False
        for path in [
            paths.SAVE_INSTANCE_META.format(id=1),
            paths.SAVE_INSTANCE_SYSTEM_DATA.format(id=1),
            paths.SAVE_INSTANCE_USER_DATA.format(id=1),
            paths.SAVE_INSTANCE_SYSTEM_DATA.format(id=2),
            paths.SAVE_INSTANCE_USER_DATA.format(id=2),
            paths.SAVE_INSTANCE_META.format(id=5),
        ]
    )
    shutil.copy(
        str(importlib.resources.files("tests") / "db"), paths.DATABASE_FILE
    )

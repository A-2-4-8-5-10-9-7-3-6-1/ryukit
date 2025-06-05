import importlib
import importlib.resources
import pathlib
import shutil

from pytest import fixture

from ryukit.app.__context__ import SYSTEM_CONFIGS
from ryukit.libs import paths

__all__ = ["seed"]


@fixture
def seed():
    any(
        (
            shutil.rmtree(path, ignore_errors=True),
            (
                path.mkdir(parents=True, exist_ok=True)
                if isinstance(path, pathlib.Path)
                else None
            ),
        )
        and False
        for path in (
            pathlib.Path(paths.DATABASE_FILE).parent,
            pathlib.Path(paths.TRACKER_FILE).parent,
            paths.RYUJINX_DIST_DIR,
            paths.RYUJINX_DATA_DIR,
        )
    )
    SYSTEM_CONFIGS["ryujinx_install"]["paths"].update(
        {
            "dist": paths.RYUJINX_DIST_DIR,
            "registered": f"{paths.RYUJINX_DATA_DIR}/bis/system/Contents/registered",
            "keys": f"{paths.RYUJINX_DATA_DIR}/system",
        }
    )
    SYSTEM_CONFIGS["save_buckets"].update(
        {
            "flow": {
                paths.SAVE_INSTANCE_META: f"{paths.RYUJINX_DATA_DIR}/bis/user/saveMeta",
                paths.SAVE_INSTANCE_USER_DATA: f"{paths.RYUJINX_DATA_DIR}/bis/user/save",
                paths.SAVE_INSTANCE_SYSTEM_DATA: f"{paths.RYUJINX_DATA_DIR}/bis/system/save",
            }
        }
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

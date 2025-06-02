import importlib
import importlib.resources
import pathlib
import shutil
import tempfile

from pytest import fixture

from ryukit.app.__context__ import INTERNAL_CONFIGS
from ryukit.libs import db, paths

__all__ = ["seed"]


@fixture
def seed():
    with tempfile.TemporaryDirectory() as dir:
        paths.CONFIG_FILE = f"{dir}/ryukitconfig.json"
        paths.SAVE_INSTANCE_DIR = f"{dir}/saves/{'{id}'}"
        paths.SAVE_INSTANCE_META = f"{paths.SAVE_INSTANCE_DIR}/meta"
        paths.SAVE_INSTANCE_SYSTEM_DATA = (
            f"{paths.SAVE_INSTANCE_DIR}/registered"
        )
        paths.SAVE_INSTANCE_USER_DATA = f"{paths.SAVE_INSTANCE_DIR}/user"
        paths.RYUJINX_DIST_DIR = f"{dir}/ryujinx/dist"
        paths.RYUJINX_DATA_DIR = f"{dir}/ryujinx/data"
        paths.DATABASE_FILE = f"{dir}/db"
        db.CLIENT_CONFIGS.update(
            {"url": f"sqlite:///{paths.DATABASE_FILE}", "echo": True}
        )
        INTERNAL_CONFIGS["ryujinx_install"]["paths"].update(
            {
                "dist": paths.RYUJINX_DIST_DIR,
                "registered": f"{paths.RYUJINX_DATA_DIR}/bis/system/Contents/registered",
                "keys": f"{paths.RYUJINX_DATA_DIR}/system",
            }
        )
        INTERNAL_CONFIGS["save_buckets"].update(
            {
                "flow": {
                    paths.SAVE_INSTANCE_META: f"{paths.RYUJINX_DATA_DIR}/bis/user/saveMeta",
                    paths.SAVE_INSTANCE_USER_DATA: f"{paths.RYUJINX_DATA_DIR}/bis/user/save",
                    paths.SAVE_INSTANCE_SYSTEM_DATA: f"{paths.RYUJINX_DATA_DIR}/bis/system/save",
                }
            }
        )
        any(
            map(
                lambda _: False,
                (
                    (
                        pathlib.Path(path).mkdir(parents=True, exist_ok=True),
                        shutil.copy(
                            str(importlib.resources.files("tests") / "data"),
                            path,
                        ),
                    )
                    for path in [
                        paths.SAVE_INSTANCE_META.format(id=1),
                        paths.SAVE_INSTANCE_SYSTEM_DATA.format(id=1),
                        paths.SAVE_INSTANCE_USER_DATA.format(id=1),
                        paths.SAVE_INSTANCE_SYSTEM_DATA.format(id=2),
                        paths.SAVE_INSTANCE_USER_DATA.format(id=2),
                        paths.SAVE_INSTANCE_META.format(id=5),
                    ]
                ),
            )
        )
        shutil.copy(
            str(importlib.resources.files("tests") / "db"), paths.DATABASE_FILE
        )
        yield

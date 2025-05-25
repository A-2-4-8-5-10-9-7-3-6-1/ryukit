import datetime
import importlib
import importlib.resources
import os
import shutil
import tempfile

from pytest import fixture

from ryukit.app.__context__ import INTERNAL_CONFIGS, INTERSESSION_STATE
from ryukit.libs import db, paths

__all__ = ["seed", "verify_setup"]


@fixture(autouse=True)
def verify_setup():
    for var in ["RYUKIT_INSTALL_URL"]:
        if os.environ.get(var):
            continue
        raise RuntimeError(f"Missing env variable '{var}'.")


@fixture
def seed():
    with tempfile.TemporaryDirectory() as temp_dir:
        paths.CONFIG_FILE = f"{temp_dir}/ryukitconfig.json"
        paths.SAVE_INSTANCE_DIR = f"{temp_dir}/saves/{'{id}'}"
        paths.SAVE_INSTANCE_META = f"{paths.SAVE_INSTANCE_DIR}/meta"
        paths.SAVE_INSTANCE_SYSTEM_DATA = (
            f"{paths.SAVE_INSTANCE_DIR}/registered"
        )
        paths.SAVE_INSTANCE_USER_DATA = f"{paths.SAVE_INSTANCE_DIR}/user"
        paths.STATE_FILE = f"{temp_dir}/state"
        paths.RYUJINX_DIST_DIR = f"{temp_dir}/ryujinx/dist"
        paths.RYUJINX_DATA_DIR = f"{temp_dir}/ryujinx/data"
        paths.DATABASE_FILE = f"{temp_dir}/db"
        db.CLIENT_CONFIGS.update(
            {"url": f"sqlite:///{paths.DATABASE_FILE}", "echo": True}
        )
        INTERSESSION_STATE.update({"ryujinx_meta": {"KEY": "VALUE"}})
        INTERNAL_CONFIGS.update(
            {
                "ryujinx_install": {
                    "sha256": "3e841a946595abc56c02409e165c62cb8e049963b54853dc551b2918e1f25d17",
                    "paths": {
                        "dist": paths.RYUJINX_DIST_DIR,
                        "registered": f"{paths.RYUJINX_DATA_DIR}/bis/system/Contents/registered",
                        "keys": f"{paths.RYUJINX_DATA_DIR}/system",
                    },
                },
                "save_buckets": {
                    "flow": {
                        paths.SAVE_INSTANCE_META: f"{paths.RYUJINX_DATA_DIR}/bis/user/saveMeta",
                        paths.SAVE_INSTANCE_USER_DATA: f"{paths.RYUJINX_DATA_DIR}/bis/user/save",
                        paths.SAVE_INSTANCE_SYSTEM_DATA: f"{paths.RYUJINX_DATA_DIR}/bis/system/save",
                    }
                },
            }
        )
        shutil.copytree(
            str(importlib.resources.files("tests.data") / "saves"),
            f"{temp_dir}/saves",
        )
        with db.client() as client:
            any(
                client.add(db.RyujinxSave(**data))
                for data in [
                    {
                        "id": 1,
                        "label": "save20250524131236",
                        "created": datetime.datetime(2025, 5, 24, 13, 12, 36),
                        "updated": datetime.datetime(2025, 5, 24, 13, 12, 36),
                        "last_used": None,
                        "size": 236666670,
                    },
                    {
                        "id": 2,
                        "label": "save20250524131239",
                        "created": datetime.datetime(2025, 5, 24, 13, 12, 39),
                        "updated": datetime.datetime(2025, 5, 24, 13, 12, 39),
                        "last_used": None,
                        "size": 157777780,
                    },
                    {
                        "id": 3,
                        "label": "LABELLED",
                        "created": datetime.datetime(2025, 5, 24, 13, 13, 0),
                        "updated": datetime.datetime(2025, 5, 24, 13, 13, 0),
                        "last_used": None,
                        "size": 0,
                    },
                    {
                        "id": 4,
                        "label": "save20250524131307",
                        "created": datetime.datetime(2025, 5, 24, 13, 13, 7),
                        "updated": datetime.datetime(2025, 5, 24, 13, 13, 7),
                        "last_used": None,
                        "size": 0,
                    },
                    {
                        "id": 5,
                        "label": "RELABELLED",
                        "created": datetime.datetime(2025, 5, 24, 13, 13, 14),
                        "updated": datetime.datetime(
                            2025, 5, 24, 13, 13, 41, 966280
                        ),
                        "last_used": None,
                        "size": 78888890,
                    },
                ]
            )
        yield

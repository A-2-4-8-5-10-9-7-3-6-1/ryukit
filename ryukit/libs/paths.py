"""File-system definitions."""

import pathlib

import platformdirs

__all__ = [
    "CONFIG_FILE",
    "DATABASE_FILE",
    "SAVE_INSTANCE_DIR",
    "SAVE_INSTANCE_META",
    "SAVE_INSTANCE_SYSTEM_DATA",
    "SAVE_INSTANCE_USER_DATA",
    "RYUJINX_DIST_DIR",
    "RYUJINX_DATA_DIR",
]
CONFIG_FILE = str(pathlib.Path.home() / "ryukitconfig.json")
DATABASE_FILE = str(
    platformdirs.user_data_path("RyuKit", appauthor=False, roaming=True) / "db"
)
SAVE_INSTANCE_DIR = str(
    platformdirs.user_data_path("RyuKit", appauthor=False, roaming=True)
    / "saves"
    / "{id}"
)
SAVE_INSTANCE_META = str(pathlib.Path(SAVE_INSTANCE_DIR) / "meta")
SAVE_INSTANCE_SYSTEM_DATA = str(pathlib.Path(SAVE_INSTANCE_DIR) / "registered")
SAVE_INSTANCE_USER_DATA = str(pathlib.Path(SAVE_INSTANCE_DIR) / "user")
RYUJINX_DIST_DIR = platformdirs.user_data_dir(
    "Ryujinx-1.1.1393-win_x64", appauthor=False
)
RYUJINX_DATA_DIR = platformdirs.user_data_dir(
    "Ryujinx", appauthor=False, roaming=True
)
TRACKER_FILE = str(
    platformdirs.user_cache_path(appname="RyuKit", appauthor=False) / "tracker"
)

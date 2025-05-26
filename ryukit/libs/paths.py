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
    "STATE_FILE",
    "RYUJINX_DIST_DIR",
    "RYUJINX_DATA_DIR",
]
CONFIG_FILE = f"{pathlib.Path.home()}/ryukitconfig.json"
DATABASE_FILE = (
    f"{platformdirs.user_data_dir("RyuKit", appauthor=False, roaming=True)}/db"
)
SAVE_INSTANCE_DIR = f"{platformdirs.user_data_dir("RyuKit", appauthor=False, roaming=True)}/saves/{'{id}'}"
SAVE_INSTANCE_META = f"{SAVE_INSTANCE_DIR}/meta"
SAVE_INSTANCE_SYSTEM_DATA = f"{SAVE_INSTANCE_DIR}/registered"
SAVE_INSTANCE_USER_DATA = f"{SAVE_INSTANCE_DIR}/user"
STATE_FILE = f"{platformdirs.user_data_dir("RyuKit", appauthor=False, roaming=True)}/state"
RYUJINX_DIST_DIR = platformdirs.user_data_dir(
    "Ryujinx-{appVersion}-{targetSystem}", appauthor=False
)
RYUJINX_DATA_DIR = platformdirs.user_data_dir(
    "Ryujinx", appauthor=False, roaming=True
)

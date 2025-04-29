"""File-system definitions."""

import enum
import pathlib

import platformdirs

__all__ = ["File"]


class File(str, enum.Enum):
    ROAMING_DATA = platformdirs.user_data_dir(
        "RyuKit", roaming=True, appauthor=False
    )
    CONFIG_FILE = f"{pathlib.Path.home()}/ryukit_configs.json"
    DATABASE_FILE = f"{platformdirs.user_data_dir("RyuKit", appauthor=False, roaming=True)}/db"
    SAVE_INSTANCE_DIR = f"{platformdirs.user_data_dir("RyuKit", appauthor=False, roaming=True)}/saves/{'{instance_id}'}"
    SAVE_INSTANCE_META = f"{SAVE_INSTANCE_DIR}/meta"
    SAVE_INSTACE_SYSTEM_DATA = f"{SAVE_INSTANCE_DIR}/registered"
    SAVE_INSTANCE_USER_DATA = f"{SAVE_INSTANCE_DIR}/user"
    STATE_FILE = f"{platformdirs.user_data_dir("RyuKit", appauthor=False, roaming=True)}/state"
    RYUJINX_DIST_DIR = platformdirs.user_data_dir(
        "Ryujinx-{version}-{target_system}", appauthor=False
    )
    RYUJINX_DATA_DIR = platformdirs.user_data_dir("Ryujinx", appauthor=False)

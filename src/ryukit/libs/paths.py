"""File-system definitions."""

import pathlib

import platformdirs

__all__ = [
    "DATABASE_FILE",
    "SAVE_INSTANCE_DIR",
    "SAVE_INSTANCE_META",
    "SAVE_INSTANCE_SYSTEM_DATA",
    "SAVE_INSTANCE_USER_DATA",
    "RYUJINX_DIST_DIR",
    "RYUJINX_DATA_DIR",
    "TRACKER_FILE",
]
DATABASE_FILE = str(
    platformdirs.user_data_path("RyuKit", appauthor=False, roaming=True) / "db"
)
"""Path to database file."""
SAVE_INSTANCE_DIR = str(
    platformdirs.user_data_path("RyuKit", appauthor=False, roaming=True)
    / "saves"
    / "{id}"
)
"""
Path to a save-instance's directory.

- id: ID of the save bucket to access.
"""
SAVE_INSTANCE_META = str(pathlib.Path(SAVE_INSTANCE_DIR) / "meta")
"""
Path to save-instance's 'meta' directory.

- id: ID of the save bucket to access.
"""
SAVE_INSTANCE_SYSTEM_DATA = str(pathlib.Path(SAVE_INSTANCE_DIR) / "registered")
"""
Path to save-instance's 'registered' directory.

- id: ID of the save bucket to access.
"""
SAVE_INSTANCE_USER_DATA = str(pathlib.Path(SAVE_INSTANCE_DIR) / "user")
"""
Path to save-instance's 'user' directory.

- id: ID of the save bucket to access.
"""
RYUJINX_DIST_DIR = platformdirs.user_data_dir(
    "Ryujinx-1.1.1393-win_x64", appauthor=False
)
"""Path Ryujinx-executable's directory."""
RYUJINX_DATA_DIR = platformdirs.user_data_dir(
    "Ryujinx", appauthor=False, roaming=True
)
"""Path to Ryujinx's data directory."""
TRACKER_FILE = str(
    platformdirs.user_cache_path(appname="RyuKit", appauthor=False) / "tracker"
)
"""Path to app's tracker file."""

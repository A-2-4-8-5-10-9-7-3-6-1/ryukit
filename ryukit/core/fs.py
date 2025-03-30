"""File-system definitions."""

import enum
import os
import pathlib
import typing

import platformdirs

__all__ = ["File"]

# ==== File Resolution ====

dynamic_paths: dict[str, pathlib.Path | str] = {
    "roaming_app_data": platformdirs.PlatformDirs(
        appname="RyuKit", roaming=True
    ).user_data_path,
    "configs_file": platformdirs.user_config_path() / "ryukit-config.json",
}

if os.environ.get("RYUKIT_ENV") == "DEV":
    dynamic_paths["roaming_app_data"] = ".ryukit/roaming" / typing.cast(
        pathlib.Path, dynamic_paths["roaming_app_data"]
    ).relative_to(platformdirs.user_data_path(roaming=True))
    dynamic_paths["configs_file"] = ".ryukit/ryukit-config.json"


class File(enum.Enum):
    ROAMING_APP_DATA = dynamic_paths["roaming_app_data"]
    CONFIG_FILE = dynamic_paths["configs_file"]
    DATABASE = f"{ROAMING_APP_DATA}/.db"

    def __init__(self, stem: pathlib.Path | str):
        self._stem = stem

    def __call__(self, **kwargs: str):
        """
        Generate file path.

        :param kwargs: Keywords for path construction.

        :returns: The path corresponding to the `File` object.
        """

        if isinstance(self._stem, pathlib.Path):
            return self._stem

        return pathlib.Path(self._stem.format(**kwargs))

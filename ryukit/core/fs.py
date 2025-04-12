"""File-system definitions."""

import enum
import os
import pathlib

import platformdirs

__all__ = ["File"]


# MARK: File Resolution

dynamic_paths: dict[str, pathlib.Path | str] = {
    "local_data_dir": platformdirs.user_data_dir(),
    "roaming_data_dir": platformdirs.user_data_dir(roaming=True),
    "configs_file": platformdirs.user_config_path() / "ryukit-config.json",
}

if os.environ.get("RYUKIT_DEV_FILES", "").lower() == "true":
    dynamic_paths |= {
        "local_data_dir": ".ryukit/local",
        "roaming_data_dir": ".ryukit/roaming",
        "configs_file": ".ryukit/ryukit-config.json",
    }


class File(enum.Enum):
    LOCAL_DATA_DIR = dynamic_paths["local_data_dir"]
    ROAMING_DATA_DIR = dynamic_paths["roaming_data_dir"]
    ROAMING_APP_DATA = ROAMING_DATA_DIR / platformdirs.user_data_path(
        "RyuKit"
    ).relative_to(platformdirs.user_data_path())
    CONFIG_FILE = dynamic_paths["configs_file"]
    DATABASE = f"{ROAMING_APP_DATA}/database.db"

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

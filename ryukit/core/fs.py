"""File-system definitions."""

import enum
import pathlib

import platformdirs

__all__ = ["File"]


class File(enum.Enum):
    LOCAL_DATA_DIR = platformdirs.user_data_dir()
    ROAMING_DATA_DIR = platformdirs.user_data_dir(roaming=True)
    ROAMING_APP_DATA_DIR = platformdirs.user_data_path(
        "RyuKit", roaming=True, appauthor=False
    )
    CONFIG_FILE = (
        platformdirs.user_config_path("RyuKit", appauthor=False, roaming=True)
        / "ryukit-config.json"
    )
    DATABASE_FILE = f"{ROAMING_APP_DATA_DIR}/db"
    SAVE_INSTANCE_FOLDER = f"{ROAMING_APP_DATA_DIR}/saves/{"{instance_id}"}"
    STATE_FILE = ROAMING_APP_DATA_DIR / "configs"

    def __init__(self, stem: pathlib.Path | str):
        self._stem = stem

    def __call__(self, **kwargs: object):
        """
        Generate path to corresponding file-system object.

        :param kwargs: Keywords for path construction.
        :returns: Path corresponding to file-system object.
        """

        if isinstance(self._stem, pathlib.Path):
            return self._stem
        return pathlib.Path(self._stem.format(**kwargs))

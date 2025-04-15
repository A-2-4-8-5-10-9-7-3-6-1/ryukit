"""Runtime-management utilities."""

import collections
import collections.abc
import dataclasses
import functools
import importlib
import importlib.resources
import json
import sqlite3
import typing

import jsonschema

from . import db, fs

__all__ = ["context", "with_context"]


@dataclasses.dataclass
class Context:
    configs: dict[str, object]
    persistence_layer: dict[str, object]
    goo: dict[str, object]
    internal_layer: dict[str, object]


context = Context(
    {},
    {},
    {},
    internal_layer=json.loads(
        importlib.resources.read_text(
            "ryukit",
            "assets",
            "configs",
            "internal-configs.json",
            encoding="utf-8",
        )
    ),
)


def with_context[**P, R](process: collections.abc.Callable[P, R]):
    """
    Adds a runtime-context load step to the start of a process.

    :param process: The process to extend.

    :returns: The extended process.
    """

    @functools.wraps(process)
    def inner(*args: P.args, **kwargs: P.kwargs):
        context.configs = json.loads(
            fs.File.CONFIG_FILE().read_bytes()
            if fs.File.CONFIG_FILE().exists()
            else importlib.resources.read_binary(
                "ryukit", "assets", "configs", "default-app-configs.json"
            )
        )

        context.configs.pop("$schema", None)

        try:
            typing.cast(
                typing.Any,
                jsonschema.Draft7Validator(
                    json.loads(
                        importlib.resources.read_text(
                            "ryukit",
                            "assets",
                            "schemas",
                            "app-configs.schema.json",
                            encoding="utf-8",
                        )
                    )
                ),
            ).validate(context.configs)

        except jsonschema.ValidationError as e:
            context.goo = {"error": e}

            return process(*args, **kwargs)

        for *key, default in map(
            lambda args: map(str, args),
            [
                (
                    "ryujinxConfigs",
                    "distDir",
                    fs.File.LOCAL_DATA_DIR()
                    / typing.cast(
                        str,
                        typing.cast(
                            dict[str, object],
                            context.internal_layer["ryujinxInstall"],
                        )["defaultDistDirSuffix"],
                    ),
                ),
                (
                    "ryujinxConfigs",
                    "roamingDataDir",
                    fs.File.ROAMING_DATA_DIR()
                    / typing.cast(
                        str,
                        typing.cast(
                            dict[str, object],
                            context.internal_layer["ryujinxInstall"],
                        )["defaultRoamingDirSuffix"],
                    ),
                ),
            ],
        ):
            setting: dict[str, object] = context.configs
            *prefix, suffix = key

            for part in prefix:
                setting = typing.cast(typing.Any, setting[part])

            setting[suffix] = setting.get(suffix) or default

        fs.File.ROAMING_APP_DATA_DIR().mkdir(parents=True, exist_ok=True)

        context.persistence_layer = json.loads(
            fs.File.STATE_FILE().read_bytes()
            if fs.File.STATE_FILE().exists()
            else importlib.resources.read_binary(
                "ryukit", "assets", "configs", "initial-state.json"
            )
        )

        with db.theme(sqlite3.connect)("DATABASE") as conn:
            conn.executescript(
                importlib.resources.read_text(
                    "ryukit", "assets", "setup_database.sql", encoding="utf-8"
                )
            )

        try:
            return process(*args, **kwargs)

        finally:
            fs.File.STATE_FILE().write_text(
                json.dumps(context.persistence_layer)
            )
            fs.File.CONFIG_FILE().write_text(
                json.dumps(context.configs, indent=2)
            )

    return inner

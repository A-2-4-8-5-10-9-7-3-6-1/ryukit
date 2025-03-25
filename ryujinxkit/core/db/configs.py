"""Database-related configurations."""

import typing


class ConfigDefaults(typing.TypedDict):
    save_tag: str


class Configs(typing.TypedDict):
    defaults: ConfigDefaults


DB_CONFIGS: Configs = {"defaults": {"save_tag": "none"}}

import typing


class _Defaults(typing.TypedDict):
    save_tag: str


class _Configs(typing.TypedDict):
    defaults: _Defaults


DB_CONFIGS: _Configs = {
    "defaults": {
        "save_tag": "none",
    },
}

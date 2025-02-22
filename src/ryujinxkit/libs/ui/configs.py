import typing


class _TyperConfigs(typing.TypedDict, total=False):
    rich_markup_mode: typing.Literal["markdown", "rich", None]
    rich_help_panel: str | None
    pretty_exceptions_enable: bool
    pretty_exceptions_show_locals: bool
    pretty_exceptions_short: bool


class _UIConfigs(typing.TypedDict):
    refresh_rate: int
    typer_settings: _TyperConfigs


UI_CONFIGS: _UIConfigs = {
    "refresh_rate": 10,
    "typer_settings": {
        "rich_markup_mode": None,
    },
}

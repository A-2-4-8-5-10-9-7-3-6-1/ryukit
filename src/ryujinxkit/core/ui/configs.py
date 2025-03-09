"""UI-related configurations.

Exports
-------
- UI_CONFIGS: UI configuration object.
"""

import typing


class TyperConfigs(typing.TypedDict, total=False):
    rich_markup_mode: typing.Literal["markdown", "rich", None]
    rich_help_panel: str | None
    pretty_exceptions_enable: bool
    pretty_exceptions_show_locals: bool
    pretty_exceptions_short: bool


class UIConfigs(typing.TypedDict):
    refresh_rate: int
    typer_settings: TyperConfigs


UI_CONFIGS: UIConfigs = {
    "refresh_rate": 10,
    "typer_settings": {"rich_markup_mode": None},
}

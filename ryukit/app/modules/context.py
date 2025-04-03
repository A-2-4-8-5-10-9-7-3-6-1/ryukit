"""Context module for app commands."""

import dataclasses
import importlib
import importlib.resources
import json

import typer

from ...core import ui

__all__ = ["states", "root_typer", "manage_typer", "internal_configs"]

# ==== State ====


@dataclasses.dataclass
class StateManager:
    configs: dict[str, object] = dataclasses.field(default_factory=lambda: {})


states = StateManager()

# ==== Information ====

internal_configs: dict[str, object] = json.loads(
    (
        importlib.resources.files("ryukit")
        / "assets"
        / "configs"
        / "internal.json"
    ).read_bytes()
)

# ==== Typers ====

root_typer = ui.theme_applier(typer.Typer)(name="ryukit")
manage_typer = ui.theme_applier(typer.Typer)(name="manage")

root_typer.add_typer(manage_typer)

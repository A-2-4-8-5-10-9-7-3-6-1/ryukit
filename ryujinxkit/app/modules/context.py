"""Context module for app commands."""

import dataclasses

import typer

from ...core import ui

__all__ = ["states", "root_typer", "manage_typer"]

# ==== State ====


@dataclasses.dataclass
class StateManager:
    configs: dict[str, object] = dataclasses.field(default_factory=lambda: {})


states = StateManager()

# ==== Typers ====

root_typer = ui.theme_applier(typer.Typer)(name="ryujinxkit")
manage_typer = ui.theme_applier(typer.Typer)(name="manage")

root_typer.add_typer(manage_typer)

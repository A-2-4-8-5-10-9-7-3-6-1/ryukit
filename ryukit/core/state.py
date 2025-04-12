"""Utilities for managing shared command state."""

import dataclasses
import importlib
import importlib.resources
import json

__all__ = ["states", "internal_configs"]


# MARK: Mutable State


@dataclasses.dataclass
class StateManager:
    configs: dict[str, object] = dataclasses.field(default_factory=lambda: {})


states = StateManager()


# MARK: Internal State

internal_configs: dict[str, object] = json.loads(
    importlib.resources.read_text(
        "ryukit",
        "assets",
        "configs",
        "internal-configs.json",
        encoding="utf-8",
    )
)

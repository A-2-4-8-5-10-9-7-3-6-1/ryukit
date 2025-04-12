"""Objects shared amongst commands."""

import dataclasses
import importlib
import importlib.resources
import json

__all__ = ["states", "internal_configs"]


# MARK: State Management


@dataclasses.dataclass
class StateManager:
    configs: dict[str, object] = dataclasses.field(default_factory=lambda: {})


states = StateManager()


# MARK: Internal Configurations

internal_configs: dict[str, object] = json.loads(
    importlib.resources.read_text(
        "ryukit", "assets", "configs", "internal.json", encoding="utf-8"
    )
)

"""UI-related objects."""

import rich
import rich.console
import rich.style
import rich.text
import rich.theme

_theme_extras = {
    "colour.primary": "blue",
    "colour.secondary": "none",
    "colour.accent": "red",
}
console = rich.console.Console(
    theme=rich.theme.Theme(
        {
            "error": "red bold",
            "markdown.link_url": _theme_extras["colour.accent"],
            **_theme_extras,
        }
    ),
    style="colour.secondary",
    highlight=False,
)

"""UI-related objects.

Exports
-------
- console: App's main console.
"""

import rich
import rich.console
import rich.style
import rich.text
import rich.theme

theme_dict = {
    "colour.primary": "blue",
    "colour.secondary": "none",
    "colour.accent": "red",
}
console = rich.console.Console(
    theme=rich.theme.Theme(
        {
            "error": "red bold",
            "markdown.link_url": theme_dict["colour.accent"],
            **theme_dict,
        }
    ),
    style="colour.secondary",
    highlight=False,
)

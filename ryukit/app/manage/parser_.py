import typer

from ...core import ui

__all__ = ["app"]
app = ui.theme_applier(typer.Typer)(name="manage")


@app.callback()
def _():
    """Manage your data."""

    pass

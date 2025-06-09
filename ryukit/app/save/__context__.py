import typer

from ...utils import qol
from ..__context__ import app

__all__ = ["command"]


@qol.use
def command():
    save = typer.Typer(name="save")
    app.add_typer(save)
    func = save.command

    @save.callback()
    def _():
        """Manage save buckets."""

    return func

import typer

from ...utils import qol
from ..__context__ import app

__all__ = ["command"]


@qol.use
def command():
    """Command decorator of app's save subtyper."""

    save = typer.Typer(name="save")
    app.add_typer(save)
    func = save.command

    @save.callback()
    def _():
        """Manage save buckets."""

    return func

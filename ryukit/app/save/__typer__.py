import typer

from ...core import display
from .. import __typer__

__all__ = ["save"]
save = display.tuned(typer.Typer)(name="save")
__typer__.app.add_typer(save)


@save.callback()
def command():
    "Manage your save buckets."

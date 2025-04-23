import typer

from .. import __typer__

__all__ = ["save"]
save = typer.Typer(name="save")
__typer__.app.add_typer(save)


@save.callback()
def command():
    "Manage your save buckets."

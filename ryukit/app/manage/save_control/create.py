import datetime
import typing

import typer

from ....core import ui

__all__ = ["app"]
app = ui.theme_applier(typer.Typer)()
default_label = f"Save{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}"


@app.command("create-save", rich_help_panel="Save Control")
def _(
    label: typing.Annotated[
        str, typer.Argument(help="A label for the save.")
    ] = default_label,
):
    """Create an empty save bucket."""

    ...

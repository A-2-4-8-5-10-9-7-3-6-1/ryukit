import datetime
import typing

import typer

from ....modules import context

__all__ = []
default_label = f"Save{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}"


@context.manage_typer.command("create-save", rich_help_panel="Save Control")
def _(
    label: typing.Annotated[
        str, typer.Argument(help="A label for the save.", show_default=True)
    ] = default_label,
):
    """Create an empty save bucket."""

    ...

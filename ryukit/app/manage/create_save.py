import datetime
import typing

import typer

from ...helpers import typer_builder

__all__ = ["typer_builder_args"]
default_label = f"Save{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}"


def command(
    label: typing.Annotated[
        str, typer.Argument(help="A label for the save.")
    ] = default_label,
):
    """Create an empty save bucket."""

    ...


typer_builder_args: typer_builder.TyperBuilderArgs = {
    "command": command,
    "typer_args": [{"rich_help_panel": "Save Control"}],
}

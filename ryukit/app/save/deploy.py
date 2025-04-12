import typing

import typer

from ...helpers import typer_builder

__all__ = ["typer_builder_args"]


def command(
    id_: typing.Annotated[
        int,
        typer.Argument(
            metavar="ID",
            help="ID of bucket to deploy from.",
            show_default=False,
        ),
    ],
):
    """Deploy from a save bucket to Ryujinx."""


typer_builder_args: typer_builder.TyperBuilderArgs = {"command": command}

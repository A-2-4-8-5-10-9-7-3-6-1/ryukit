import typing

import typer

from ...helpers import typer_builder

__all__ = ["typer_builder_args"]


def command(
    id_: typing.Annotated[
        int,
        typer.Argument(
            metavar="ID",
            help="ID of bucket bucket to pull into.",
            show_default=False,
        ),
    ],
):
    """Pull data from Ryujinx into a save bucket."""


typer_builder_args: typer_builder.TyperBuilderArgs = {"command": command}

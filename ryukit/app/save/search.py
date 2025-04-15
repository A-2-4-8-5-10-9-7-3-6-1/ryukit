import typing

import typer

from ...utils import typer_builder

__all__ = ["typer_builder_args"]


def command(
    keywords: typing.Annotated[
        list[str],
        typer.Argument(help="A keyword that describes your save bucket."),
    ],
):
    """Search for a save bucket."""


typer_builder_args: typer_builder.BuilderArgs = {"command": command}

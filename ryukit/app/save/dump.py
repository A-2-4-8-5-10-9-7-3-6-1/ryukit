import typing

import typer

from ...helpers import typer_builder

__all__ = ["typer_builder_args"]


def command(
    file: typing.Annotated[
        str, typer.Argument(help="Name for dump file.")
    ] = "ryukit.dmp",
):
    """Dump your save buckets into a recovery file."""


typer_builder_args: typer_builder.TyperBuilderArgs = {"command": command}

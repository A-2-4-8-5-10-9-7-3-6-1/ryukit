from ...utils import typer_builder

__all__ = ["typer_builder_args"]


def command():
    """List your save buckets."""


typer_builder_args: typer_builder.TyperBuilderArgs = {"command": command}

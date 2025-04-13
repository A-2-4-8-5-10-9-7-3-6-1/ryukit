import importlib
import importlib.metadata
import importlib.resources
import typing

import jsonschema
import typer

from ..core import runtime, ui
from ..utils import typer_builder

__all__ = ["typer_builder_args"]


def command(
    ctx: typer.Context,
    show_configs: typing.Annotated[
        bool, typer.Option("--configs", help="Show configurations and exit.")
    ] = False,
):
    "A CLI tool for Ryujinx."

    if "error" in runtime.context.goo:
        error = typing.cast(
            jsonschema.ValidationError, runtime.context.goo["error"]
        )

        ui.console.print(
            f"[error]Malformed configuration file; {error.message}.",
            f"└── [italic]Error originated from {error.json_path}.",
            sep="\n",
        )

        raise typer.Exit(1)

    for do, command in [
        (
            show_configs,
            lambda: ui.console.print_json(data=runtime.context.configs),
        ),
        (
            not ctx.invoked_subcommand,
            lambda: ui.console.print(
                *(
                    f"[blue]{line[:25]}[/][red]{line[25:]}[/]"
                    for line in importlib.resources.read_text(
                        "ryukit", "assets", "logo.txt", encoding="utf-8"
                    ).splitlines()
                ),
                f"\nVERSION {importlib.metadata.version("ryukit")}",
                sep="\n",
                end="\n\n",
                new_line_start=True,
            ),
        ),
    ]:
        if not do:
            continue

        command()

        raise typer.Exit()


typer_builder_args: typer_builder.TyperBuilderArgs = {
    "command": command,
    "typer_args": [{"invoke_without_command": True}],
}

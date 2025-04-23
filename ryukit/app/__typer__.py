import importlib
import importlib.metadata
import importlib.resources
import typing

import jsonschema
import typer

from ..core import display, runtime

__all__ = ["app"]
app = typer.Typer(name="ryukit")


@app.callback(invoke_without_command=True)
def _(
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
        display.console.print(
            f"[error]Malformed configuration file; {error.message}.",
            f"└── [italic]Error originated from {error.json_path}.",
            sep="\n",
        )
        raise typer.Exit(1)
    for do, command in [
        (
            show_configs,
            lambda: display.console.print_json(data=runtime.context.configs),
        ),
        (
            not ctx.invoked_subcommand,
            lambda: display.console.print(
                *(
                    f"[blue]{line[:25]}[/][red]{line[25:]}[/]"
                    for line in importlib.resources.read_text(
                        "ryukit.assets", resource="logo.txt"
                    ).splitlines()
                ),
                "",
                f"VERSION {importlib.metadata.version("ryukit")}",
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

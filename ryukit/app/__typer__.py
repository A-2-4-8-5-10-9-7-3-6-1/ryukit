import importlib
import importlib.metadata
import typing

import jsonschema
import typer

from ..core import display, runtime

__all__ = ["app"]
app = display.tuned(typer.Typer)(name="ryukit")


@app.callback(no_args_is_help=True, invoke_without_command=True)
def _(
    version: typing.Annotated[
        bool, typer.Option("--version", help="Show version and exit.")
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
            version,
            lambda: display.console.print(
                f"RyuKit version {importlib.metadata.version("ryukit")}"
            ),
        )
    ]:
        if not do:
            continue
        command()
        raise typer.Exit()

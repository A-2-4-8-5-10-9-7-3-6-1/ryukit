from typing import Annotated

import typer

from ...app.save.__context__ import bucket, command, console

__all__ = ["relabel"]


@command("relabel")
def relabel(
    bucket_: Annotated[
        int,
        typer.Argument(
            metavar="BUCKET",
            help="ID of bucket to update.",
            show_default=False,
        ),
    ],
    as_: Annotated[
        str,
        typer.Option(
            "--as", help="New label for the bucket.", show_default=False
        ),
    ],
):
    """Relabel an existing bucket."""

    with bucket(bucket_) as (_, save):
        save.label = as_
    console.print("Label updated.")

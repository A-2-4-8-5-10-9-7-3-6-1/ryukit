import sqlite3
import typing

import rich
import typer

from ...core import db, fs, presentation
from ...utils import calculator, common_logic, typer_builder

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

    console = presentation.theme(rich.console.Console)()

    with db.theme(sqlite3.connect)("DATABASE") as conn:
        if not conn.execute(
            """
            SELECT
                COUNT(*)
            FROM
                ryujinx_saves
            WHERE
                id = :id;
            """,
            {"id": id_},
        ).fetchone()[0]:
            console.print("[error]No such save.")

            raise typer.Exit(1)

        try:
            common_logic.channel_save_bucket(id_, upstream=False)

        except RuntimeError:
            console.print(
                "[error]Failed to apply save.",
                "└── [italic]Is Ryujinx installed?",
                sep="\n",
            )

            raise typer.Exit(1)

        size = sum(
            path.stat().st_size if path.is_file() else 0
            for path in fs.File.SAVE_INSTANCE_FOLDER(instance_id=id_).glob(
                "**"
            )
        )

        conn.execute(
            """
            UPDATE
                ryujinx_saves
            SET
                size = :size
            WHERE
                id = :id;
            """,
            {"id": id_, "size": size},
        )

    console.print(
        "Updated bucket.",
        f"└── [italic]Bucket is now of size {calculator.megabytes(size):.1f}MB.",
        sep="\n",
    )


typer_builder_args: typer_builder.BuilderArgs = {"command": command}

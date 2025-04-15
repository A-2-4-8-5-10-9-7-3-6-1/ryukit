import io
import json
import pathlib
import sqlite3
import tarfile
import typing

import rich
import rich.status
import typer

from ...core import db, fs, presentation
from ...utils import typer_builder

__all__ = ["typer_builder_args"]


def command(
    file: typing.Annotated[
        pathlib.Path, typer.Argument(help="Name for dump file.")
    ] = pathlib.Path("ryukit.saves.dmp"),
):
    """Dump your save buckets into a recovery file."""

    console = presentation.theme(rich.console.Console)()

    with (
        io.BytesIO() as buffer,
        tarfile.TarFile(fileobj=buffer, mode="w") as tar,
        rich.status.Status(
            "Collecting data...", spinner="dots2", spinner_style="blue"
        ),
    ):
        saves: list[db.models.RyujinxSave] = []

        with db.theme(sqlite3.connect)("DATABASE") as conn:
            for save in map(
                lambda x: typing.cast(db.models.RyujinxSave, x),
                map(
                    dict,
                    conn.execute(
                        """
                        SELECT
                            *
                        FROM
                            ryujinx_saves;
                        """
                    ),
                ),
            ):
                saves.append(save)

                if fs.File.SAVE_INSTANCE_FOLDER(
                    instance_id=save["id"]
                ).exists():
                    tar.add(
                        fs.File.SAVE_INSTANCE_FOLDER(instance_id=save["id"]),
                        arcname=f"save{save["id"]}",
                    )

        with io.BytesIO(json.dumps(saves).encode()) as save_buffer:
            info = tar.tarinfo("metadata")
            info.size = len(save_buffer.getvalue())

            tar.addfile(info, save_buffer)

        file.parent.mkdir(exist_ok=True)
        file.write_bytes(buffer.getvalue())

    console.print(f"Dump file created at {file}.")


typer_builder_args: typer_builder.BuilderArgs = {"command": command}

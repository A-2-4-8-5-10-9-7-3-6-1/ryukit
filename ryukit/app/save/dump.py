import io
import json
import pathlib
import tarfile
import typing

import rich
import rich.status
import typer

from ...core import db, display, fs
from . import __typer__

__all__ = []


@__typer__.save.command(name="dump")
def _(
    into: typing.Annotated[
        pathlib.Path, typer.Argument(help="Where to dump your buckets.")
    ] = pathlib.Path("ryukit.saves.dmp"),
):
    """Dump your save buckets into a recovery file."""

    with (
        io.BytesIO() as buffer,
        tarfile.TarFile(fileobj=buffer, mode="w") as tar,
        rich.status.Status("Collecting data...", spinner="dots2"),
    ):
        saves: list[db.models.RyujinxSave] = []
        with db.connect() as conn:
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
            info = tar.tarinfo("index")
            info.size = len(save_buffer.getvalue())
            tar.addfile(info, save_buffer)
        into.parent.mkdir(exist_ok=True)
        into.write_bytes(buffer.getvalue())
    display.console.print(f"Dump file created at {into}.")

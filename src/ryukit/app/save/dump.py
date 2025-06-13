import io
import pathlib
import tarfile
from typing import Annotated, Any

import rich
import rich.status
import sqlalchemy
import typer

from ...libs import db, paths
from ...utils import misc
from .__context__ import command

__all__ = []


@command("dump")
def _(
    into: Annotated[
        pathlib.Path, typer.Argument(help="Where to dump your buckets.")
    ] = pathlib.Path("saves.ryukitdmp"),
):
    """Dump your save buckets into a recovery file."""

    with (
        io.BytesIO() as buffer,
        tarfile.TarFile(fileobj=buffer, mode="w") as tar,
        rich.status.Status("Collecting data...", spinner="dots"),
    ):
        with db.client() as client:
            save_dicts: list[dict[str, Any]] = []
            any(
                (
                    save_dicts.append(misc.model_to_dict(save)),
                    (
                        tar.add(
                            paths.SAVE_INSTANCE_DIR.format(id=save.id),
                            arcname=f"save{save.id}",
                        )
                        if pathlib.Path(
                            paths.SAVE_INSTANCE_DIR.format(id=save.id)
                        ).exists()
                        else None
                    ),
                )
                and False
                for save in client.scalars(sqlalchemy.select(db.RyujinxSave))
            )
        with io.BytesIO(misc.json_dumps(save_dicts).encode()) as save_buffer:
            info = tar.tarinfo("index")
            info.size = len(save_buffer.getvalue())
            tar.addfile(info, save_buffer)
        into.parent.mkdir(exist_ok=True)
        into.write_bytes(buffer.getvalue())
    rich.print(f"Dump file created at '{into}'.")

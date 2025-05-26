import io
import pathlib
import tarfile
from typing import Annotated, Any

import sqlalchemy
import typer

from ... import utils
from ...app.save.__context__ import command, console
from ...libs import components, db, paths

__all__ = ["dump"]


@command("dump")
def dump(
    into: Annotated[
        pathlib.Path, typer.Argument(help="Where to dump your buckets.")
    ] = pathlib.Path("saves.ryukitdmp"),
):
    """Dump your save buckets into a recovery file."""

    with (
        io.BytesIO() as buffer,
        tarfile.TarFile(fileobj=buffer, mode="w") as tar,
        components.Status(
            "Collecting data...", spinner="dots2", spinner_style="none"
        ),
    ):
        with db.client() as client:
            save_dicts: list[dict[str, Any]] = []
            any(
                map(
                    lambda _: False,
                    (
                        (
                            save_dicts.append(utils.model_to_dict(save)),
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
                        for save in client.scalars(
                            sqlalchemy.select(db.RyujinxSave)
                        )
                    ),
                )
            )
        with io.BytesIO(utils.json_dumps(save_dicts).encode()) as save_buffer:
            info = tar.tarinfo("index")
            info.size = len(save_buffer.getvalue())
            tar.addfile(info, save_buffer)
        into.parent.mkdir(exist_ok=True)
        into.write_bytes(buffer.getvalue())
    console.print(f"Dump file created at '{into}'.")

import io
import json
import pathlib
import tarfile
from typing import Annotated

import sqlalchemy
import typer

from ... import utils
from ...app.save.__context__ import command, console
from ...libs import components, db, paths


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
            saves = client.scalars(sqlalchemy.select(db.RyujinxSave)).all()
            any(
                tar.add(
                    paths.SAVE_INSTANCE_DIR.format(instance_id=save.id),
                    arcname=f"save{save.id}",
                )
                for save in saves
                if pathlib.Path(
                    paths.SAVE_INSTANCE_DIR.format(instance_id=save.id)
                ).exists()
            )
            save_dicts = list(map(utils.model_to_dict, saves))
        any(
            save.update(
                {
                    key: save[key] and save[key].isoformat()
                    for key in ("created", "updated", "last_used")
                }
            )
            for save in save_dicts
        )
        with io.BytesIO(json.dumps(save_dicts).encode()) as save_buffer:
            info = tar.tarinfo("index")
            info.size = len(save_buffer.getvalue())
            tar.addfile(info, save_buffer)
        into.parent.mkdir(exist_ok=True)
        into.write_bytes(buffer.getvalue())
    console.print(f"Dump file created at '{into}'.")

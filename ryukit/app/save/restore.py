import datetime
import json
import pathlib
import shutil
import tarfile
import tempfile
from typing import Annotated, Any

import typer

from ...app.save.__context__ import command, console
from ...libs import components, db, paths

__all__ = ["restore"]


@command("restore")
def restore(
    dump: Annotated[
        pathlib.Path,
        typer.Argument(help="Dump file path.", exists=True, dir_okay=False),
    ],
):
    """Restore saves from a dump file."""

    with (
        components.Status(
            "Restoring buckets...", spinner="dots2", spinner_style="none"
        ),
        tempfile.TemporaryDirectory() as temp_dir,
        db.client() as client,
    ):
        with tarfile.open(dump) as tar:
            tar.extractall(temp_dir)
        saves: list[dict[str, Any]] = json.loads(
            (pathlib.Path(temp_dir) / "index").read_bytes()
        )
        for save_args in saves:
            save_args.update(
                {
                    key: save_args[key]
                    and datetime.datetime.fromisoformat(save_args[key])
                    for key in ("created", "updated", "last_used")
                }
            )
            save_path = pathlib.Path(temp_dir) / f"save{save_args.pop("id")}"
            save = db.RyujinxSave(**save_args)
            client.add(save)
            client.flush([save])
            console.print(f"Restored '{save_path.stem}' under ID '{save.id}'.")
            if not save_path.exists():
                continue
            shutil.move(save_path, paths.SAVE_INSTANCE_DIR.format(id=save.id))
    console.print(f"Added '{len(saves)}' bucket(s).")

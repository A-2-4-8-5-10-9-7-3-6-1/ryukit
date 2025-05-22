import json
import pathlib
import shutil
import tarfile
import tempfile
from typing import Annotated

import typer

from ryukit.app.save.__context__ import command, console
from ryukit.libs import components, db, paths


@command("restore")
def _(
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
        db.connect() as conn,
    ):
        with tarfile.open(dump) as tar:
            tar.extractall(temp_dir)
        saves: list[db.models.RyujinxSave] = json.loads(
            (pathlib.Path(temp_dir) / "index").read_bytes()
        )
        for save in saves:
            write_to = paths.SAVE_INSTANCE_DIR.format(
                instance_id=conn.execute(
                    """
                    INSERT INTO
                        ryujinx_saves (label, created, updated, last_used, size)
                    VALUES
                        (:label, :created, :updated, :last_used, :size)
                    """,
                    save,
                ).lastrowid
            )
            save_path = pathlib.Path(temp_dir) / f"save{save['id']}"
            if not save_path.exists():
                continue
            shutil.move(save_path, write_to)
    console.print(f"Restored '{len(saves)}' bucket(s).")

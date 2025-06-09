import datetime
import json
import pathlib
import shutil
import tarfile
import tempfile
from typing import Annotated, Any, cast

import rich
import rich.live
import rich.status
import rich.tree
import typer

from ...libs import db, paths
from .__context__ import command

__all__ = []


@command("restore")
def _(
    dump: Annotated[
        pathlib.Path,
        typer.Argument(help="Dump file path.", exists=True, dir_okay=False),
    ],
):
    """Restore saves from a dump file."""

    tree = rich.tree.Tree(
        rich.status.Status("Restoring buckets...", spinner="dots")
    )
    with (
        rich.live.Live(tree, refresh_per_second=10),
        tempfile.TemporaryDirectory() as temp_dir,
        db.client() as client,
    ):
        with tarfile.open(dump) as tar:
            tar.extractall(temp_dir)
        for save_args in cast(
            list[dict[str, Any]],
            json.loads((pathlib.Path(temp_dir) / "index").read_bytes()),
        ):
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
            tree.add(f"Restored '{save_path.stem}' under ID '{save.id}'.")
            if not save_path.exists():
                continue
            shutil.move(save_path, paths.SAVE_INSTANCE_DIR.format(id=save.id))
        tree.label = "Restoration complete."

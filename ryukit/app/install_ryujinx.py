import hashlib
import io
import math
import pathlib
import shutil
import tempfile
import zipfile
from typing import Annotated, Any

import click
import requests
import rich
import rich.live
import rich.spinner
import rich.status
import rich.table
import rich.tree
import typer

from ..utils import misc
from .__context__ import SYSTEM_CONFIGS, command

__all__ = []


@command("install_ryujinx")
def _(
    url: Annotated[
        str,
        typer.Argument(
            help="Ryujinx-download URL.",
            envvar="RYUKIT_INSTALL_URL",
            show_default=False,
        ),
    ],
):
    """
    Install Ryujinx.

    WARNING: This will overwrite pre-existing app files. Proceed with caution.
    """

    def row(*args: Any):
        table = rich.table.Table(box=None, show_header=False, padding=(0, 0))
        table.add_row(*args)
        return table

    tree = rich.tree.Tree(rich.status.Status("Installing Ryujinx..."))
    bad_content_error = click.ClickException(
        "Unrecognized content. Where'd you get your link?"
    )
    with (
        rich.live.Live(tree, refresh_per_second=10),
        tempfile.TemporaryDirectory() as dir,
    ):
        with io.BytesIO() as buffer:
            step_tree = tree.add(
                row("Connecting to server", rich.spinner.Spinner("simpleDots"))
            )
            with requests.get(url, stream=True) as response:
                if response.status_code != 200:
                    raise click.ClickException(
                        "Couldn't complete the installation due to connectivity issues."
                    )
                step_tree.label = "Connected to server."
                try:
                    total = int(response.headers["content-length"])
                    progress = 0
                    content = response.iter_content(1024)
                    parts = 40
                    step_tree = tree.add(
                        row(
                            "Downloading files",
                            rich.spinner.Spinner("simpleDots"),
                        )
                    )
                    while (percent := progress / total * 100) < 100:
                        beads = math.floor(parts * percent / 100)
                        step_tree.label = row(
                            "Downloading files",
                            rich.spinner.Spinner("simpleDots"),
                            f" [{"".join("=" if beads - i != 1 else ">" for i in range(beads))}{" " * (parts - beads)}] {misc.megabytes(int(percent * total / 100)):.1f}MB/{misc.megabytes(total):.1f}MB",
                        )
                        progress += buffer.write(next(content))
                except Exception:
                    raise bad_content_error
                step_tree.label = "Downloaded files."
            if (
                hashlib.sha256(buffer.getvalue()).hexdigest()
                != SYSTEM_CONFIGS["ryujinx_install"]["sha256"]
            ):
                raise bad_content_error
            tree.add("Verified content.")
            step_tree = tree.add(
                row("Extracting download", rich.spinner.Spinner("simpleDots"))
            )
            with zipfile.ZipFile(buffer) as zip:
                zip.extractall(dir)
        step_tree.label = "Download extracted."
        any(
            shutil.copytree(pathlib.Path(dir) / key, path, dirs_exist_ok=True)
            and False
            for key, path in SYSTEM_CONFIGS["ryujinx_install"]["paths"].items()
        )
        any(
            map(
                lambda _: False,
                map(tree.add, ["Organized files.", "Noted installation."]),
            )
        )
        tree.label = f"Installed Ryujinx to '{SYSTEM_CONFIGS['ryujinx_install']['paths']['dist']}'."

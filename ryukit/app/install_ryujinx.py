import hashlib
import io
import math
import pathlib
import shutil
import tempfile
import zipfile
from typing import Annotated, Any

import requests
import rich
import rich.live
import rich.spinner
import rich.table
import typer

from ..app.__context__ import SYSTEM_CONFIGS, command
from ..utils import misc

__all__ = []


@command("install_ryujinx")
def _(
    url: Annotated[
        str,
        typer.Argument(
            help="Ryujinx-download URL.", envvar="RYUKIT_INSTALL_URL"
        ),
    ],
):
    """
    Install Ryujinx.

    WARNING: This will overwrite pre-existing app files. Proceed with caution.
    """

    def on_live(*args: Any):
        table = rich.table.Table(
            show_header=False, pad_edge=False, padding=(0, 0)
        )
        table.add_row(*args)
        live.update(table)

    chunk_size = 1024
    with tempfile.TemporaryDirectory() as dir:
        with io.BytesIO() as buffer:
            try:
                with rich.live.Live() as live:
                    on_live(rich.spinner.Spinner("dots"), " Connecting...")
                    with requests.get(url, stream=True) as response:
                        if response.status_code != 200:
                            raise click.ClickException(
                                "Couldn't complete the installation due to connectivity problems."
                            )
                        total = int(response.headers["content-length"])
                        progress = 0
                        content = response.iter_content(chunk_size)
                        parts = 40
                        total_mb = misc.megabytes(total)
                        while (percent := progress / total * 100) < 100:
                            beads = math.floor(parts * percent / 100)
                            on_live(
                                f"Downloading files... [{"".join("=" if beads - i != 1 else ">" for i in range(beads))}{" " * (parts - beads)}] {misc.megabytes(int(percent * total / 100)):.1f}MB/{total_mb:.1f}MB"
                            )
                            buffer.write(next(content))
                            progress += chunk_size
                        on_live("Downloaded files.")
                if (
                    hashlib.sha256(buffer.getvalue()).hexdigest()
                    != SYSTEM_CONFIGS["ryujinx_install"]["sha256"]
                ):
                    raise Exception
            except Exception:
                raise click.exceptions.ClickException(
                    "Unrecognized download content.\n"
                    "└── Where'd you get your link?"
                )
            rich.print("Verified content.")
            with zipfile.ZipFile(buffer) as zip:
                zip.extractall(dir)
            rich.print("Extracted files.")
        any(
            shutil.copytree(pathlib.Path(dir) / key, path, dirs_exist_ok=True)
            and False
            for key, path in SYSTEM_CONFIGS["ryujinx_install"]["paths"].items()
        )
        rich.print(
            "Organized files.",
            "Noted installation.",
            f"Ryujinx installed to {SYSTEM_CONFIGS['ryujinx_install']['paths']['dist']}.",
            sep="\n",
        )

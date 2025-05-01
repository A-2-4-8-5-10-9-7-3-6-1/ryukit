import collections
import collections.abc
import hashlib
import io
import json
import math
import pathlib
import shutil
import tempfile
import typing
import zipfile

import requests
import rich
import rich.live
import rich.spinner
import rich.table
import typer

from ryukit.app.__context__ import (
    INTERNAL_CONFIGS,
    USER_CONFIGS,
    command,
    console,
    intersession_state,
)
from ryukit.core import components
from ryukit.utils import calculator


@command("install_ryujinx")
def _():
    """
    Install Ryujinx.

    Before using this command, set 'ryujinxInstallURL' in ryukit-config.json.

    WARNING: This will overwrite pre-existing app files. Proceed with caution.
    """

    if not USER_CONFIGS["ryujinxInstallURL"]:
        console.print(
            "[error]Command cannot be used without setting 'ryujinxInstallURL'.",
            "└── Use '--help' for more information.",
            sep="\n",
        )
        raise typer.Exit(1)
    TaskTable = typing.TypedDict(
        "TaskTable",
        {
            "refresh": collections.abc.Callable[[], None],
            "render": None | rich.table.Table,
        },
    )
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = pathlib.Path(temp_dir_str)
        with io.BytesIO() as buffer:
            try:
                live: None | rich.live.Live = None
                task_table: TaskTable = {
                    "render": None,
                    "refresh": lambda: (
                        task_table.update(
                            {
                                "render": components.Table(
                                    show_header=False,
                                    box=None,
                                    pad_edge=False,
                                    padding=(0, 0),
                                )
                            }
                        ),
                        typing.cast(rich.live.Live, live).update(
                            typing.cast(rich.table.Table, task_table["render"])
                        ),
                    )
                    and None,
                }
                chunk_size = pow(2, 10)
                with components.Live(task_table["render"]) as live:
                    task_table["refresh"]()
                    task_table["render"] = typing.cast(
                        rich.table.Table, task_table["render"]
                    )
                    task_table["render"].add_row(
                        rich.spinner.Spinner("dots2"), " Connecting..."
                    )
                    with requests.get(
                        typing.cast(str, USER_CONFIGS["ryujinxInstallURL"]),
                        stream=True,
                    ) as response:
                        if response.status_code != 200:
                            raise requests.ConnectionError
                        total = int(response.headers["content-length"])
                        progress = 0
                        content = response.iter_content(chunk_size)
                        parts = 40
                        total_mb = calculator.megabytes(total)
                        while (percent := progress / total * 100) < 100:
                            beads = math.floor(parts * percent / 100)
                            task_table["refresh"]()
                            task_table["render"].add_row(
                                f"Downloading files... [{
                                    "".join("=" if beads - i != 1 else ">" for i in range(beads))
                                }{" " * (parts - beads)}] {
                                    calculator.megabytes(int(percent * total / 100)):.1f
                                }MB/{total_mb:.1f}MB"
                            )
                            buffer.write(next(content))
                            progress += chunk_size
                        task_table["refresh"]()
                        task_table["render"].add_row("Downloaded files.")
                if (
                    hashlib.sha256(buffer.getvalue()).hexdigest()
                    != INTERNAL_CONFIGS["ryujinx_install"]["sha256"]
                ):
                    raise Exception
            except requests.ConnectionError:
                raise RuntimeError("CONNECTION_FAILED")
            except Exception:
                console.print(
                    "[error]Unrecognized download content.",
                    "└── Where'd you get your link?",
                    sep="\n",
                )
                raise typer.Exit(1)
            console.print("Verified content.")
            with zipfile.ZipFile(buffer) as zip:
                zip.extractall(temp_dir_str)
            console.print("Extracted files.")
        metadata: dict[str, object] = json.loads(
            (temp_dir / "metadata.json").read_bytes()
        )
        paths = {
            "distDir": typing.cast(
                str,
                typing.cast(dict[str, object], USER_CONFIGS["ryujinxConfigs"])[
                    "distDir"
                ],
            ).format(**metadata),
            "roamingDataDir": typing.cast(
                str,
                typing.cast(dict[str, object], USER_CONFIGS["ryujinxConfigs"])[
                    "roamingDataDir"
                ],
            ).format(**metadata),
        }
        any(
            map(
                lambda _: False,
                (
                    map(
                        lambda pair: shutil.copytree(
                            temp_dir / pair[0],
                            pathlib.Path(pair[1].format(**paths)),
                            dirs_exist_ok=True,
                        ),
                        typing.cast(
                            dict[str, str],
                            INTERNAL_CONFIGS["ryujinx_install"]["paths"],
                        ).items(),
                    )
                ),
            )
        )
        console.print("Organized files.")
        intersession_state["ryujinx_meta"] = metadata
        console.print(
            "Noted installation.",
            f"Ryujinx installed to {paths["distDir"]}.",
            sep="\n",
        )

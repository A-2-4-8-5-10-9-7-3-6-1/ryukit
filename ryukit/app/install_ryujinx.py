import collections
import collections.abc
import hashlib
import io
import json
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

from ..core import runtime, ui
from ..helpers import typer_builder

__all__ = ["typer_builder_args"]


def command():
    """
    Install Ryujinx.

    Before using this command, set 'ryujinxInstallURL' in ryujinxkit-config.json.

    [yellow]:warning:[/] This will overwrite pre-existing app files. Proceed with caution.
    """

    if not runtime.context.configs["ryujinxInstallURL"]:
        ui.console.print(
            "[error]Command cannot be used without setting 'ryujinxInstallURL'.",
            "└── [italic]Use '--help' for more information.",
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
                                "render": ui.theme_applier(rich.table.Table)(
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
                chunk_size = pow(2, 20)
                spinner = ui.theme_applier(rich.spinner.Spinner)(
                    "dots", style="colour.primary"
                )

                with ui.theme_applier(rich.live.Live)(
                    task_table["render"]
                ) as live:
                    task_table["refresh"]()

                    task_table["render"] = typing.cast(
                        rich.table.Table, task_table["render"]
                    )

                    task_table["render"].add_row(spinner, " Connecting...")

                    with requests.get(
                        typing.cast(
                            str, runtime.context.configs["ryujinxInstallURL"]
                        ),
                        stream=True,
                    ) as response:
                        if response.status_code != 200:
                            raise requests.ConnectionError

                        total = float(response.headers["content-length"])
                        progress = 0
                        content = response.iter_content(chunk_size)

                        while (percent := progress / total) < 1:
                            task_table["refresh"]()
                            task_table["render"].add_row(
                                spinner,
                                " Downloading files...",
                                f" ({percent * 100:.1f}%)",
                            )
                            buffer.write(next(content))

                            progress += chunk_size

                        task_table["refresh"]()
                        task_table["render"].add_row(
                            "[green]:heavy_check_mark:[/] Downloaded files."
                        )

                if (
                    hashlib.sha256(buffer.getvalue()).hexdigest()
                    != typing.cast(
                        dict[str, object],
                        runtime.context.internal_layer["ryujinxInstall"],
                    )["sha256"]
                ):
                    raise Exception

            except requests.ConnectionError:
                raise RuntimeError("CONNECTION_FAILED")

            except Exception:
                ui.console.print(
                    "[error]Unrecognized download content.",
                    "└── [italic]Where'd you get your link?",
                    sep="\n",
                )

                raise typer.Exit(1)

            ui.console.print(
                "[reset][green]:heavy_check_mark:", "Verified content."
            )

            with zipfile.ZipFile(buffer) as zip:
                zip.extractall(temp_dir_str)

            ui.console.print(
                "[reset][green]:heavy_check_mark:", "Extracted files."
            )

        metadata: dict[str, object] = json.loads(
            (temp_dir / "metadata.json").read_bytes()
        )
        paths = {
            "distDir": typing.cast(
                str,
                typing.cast(
                    dict[str, object],
                    runtime.context.configs["ryujinxConfigs"],
                )["distDir"],
            ).format(**metadata),
            "roamingDataDir": typing.cast(
                str,
                typing.cast(
                    dict[str, object],
                    runtime.context.configs["ryujinxConfigs"],
                )["roamingDataDir"],
            ).format(**metadata),
        }

        for source, destination in map(
            lambda pair: (pair[0], pathlib.Path(pair[1].format(**paths))),
            typing.cast(
                dict[str, str],
                typing.cast(
                    dict[str, object],
                    runtime.context.internal_layer["ryujinxInstall"],
                )["paths"],
            ).items(),
        ):
            shutil.copytree(temp_dir / source, destination, dirs_exist_ok=True)

        ui.console.print(
            "[reset][green]:heavy_check_mark:", "Organized files."
        )

        runtime.context.persistence_layer["ryujinx"] = {
            **typing.cast(
                dict[str, object], runtime.context.persistence_layer["ryujinx"]
            ),
            "meta": metadata,
        }

        ui.console.print(
            "[reset][green]:heavy_check_mark:",
            "Noted installation.",
            "\n[reset]:package:",
            f"Ryujinx was installed to {paths["distDir"]}.",
        )


typer_builder_args: typer_builder.TyperBuilderArgs = {"command": command}

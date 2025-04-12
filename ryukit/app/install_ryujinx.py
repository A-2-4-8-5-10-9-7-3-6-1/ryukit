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
import rich.progress
import typer

from ..core import runtime, ui
from ..helpers import typer_builder

__all__ = ["typer_builder_args"]


def command():
    """
    Install Ryujinx.

    Before using this command, set 'ryujinxInstallURL' in ryujinxkit-config.json.

    [yellow]:warning:[/yellow] This will overwrite pre-existing app files. Proceed with caution.
    """

    if not runtime.context.configs["ryujinxInstallURL"]:
        ui.console.print(
            "[error]Command cannot be used without setting 'ryujinxInstallURL'.",
            "└── Use '--help' for more information.",
            sep="\n",
        )

        raise typer.Exit(1)

    try:
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = pathlib.Path(temp_dir_str)

            with io.BytesIO() as buffer:
                with ui.theme_applier(rich.progress.Progress)(
                    ui.theme_applier(rich.progress.SpinnerColumn)(
                        finished_text="[green]:heavy_check_mark:"
                    ),
                    "{task.description}",
                    "({task.percentage:.1f}%)",
                ) as progress:
                    task_id = progress.add_task("Downloading files...")
                    chunk_size = pow(2, 20)

                    try:
                        with requests.get(
                            typing.cast(
                                str,
                                runtime.context.configs["ryujinxInstallURL"],
                            ),
                            stream=True,
                        ) as response:
                            if response.status_code != 200:
                                raise RuntimeError("CONNECTION_FAILED")

                            ui.console.print(
                                "Established connection.", "(1/3)"
                            )
                            progress.update(
                                task_id,
                                total=float(
                                    response.headers["content-length"]
                                ),
                            )

                            for chunk in response.iter_content(chunk_size):
                                buffer.write(chunk)
                                progress.advance(task_id, chunk_size)

                            ui.console.print("Fetched content.", "(2/3)")

                    except requests.ConnectionError:
                        raise RuntimeError("CONNECTION_FAILED")

                    if (
                        hashlib.sha256(buffer.getvalue()).hexdigest()
                        != typing.cast(
                            dict[str, object],
                            runtime.context.internal_layer["ryujinxInstall"],
                        )["sha256"]
                    ):
                        raise RuntimeError("INVALID_CONTENT")

                    ui.console.print("Verified content.", "(3/3)")

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
                shutil.copytree(
                    temp_dir / source, destination, dirs_exist_ok=True
                )

            runtime.context.persistence_layer["ryujinx"] = {
                **typing.cast(
                    dict[str, object],
                    runtime.context.persistence_layer["ryujinx"],
                ),
                "meta": metadata,
            }

            ui.console.print(
                "[reset][green]:heavy_check_mark:",
                "Organized files.",
                "\n[reset]:package:",
                f"Installed Ryujinx to {paths["distDir"]}.",
                "\nExistence of Ryujinx on your system has been noted.",
            )

    except RuntimeError as e:
        (message,) = e.args

        ui.console.print(f"[error]{message}")

        raise typer.Exit(1)


typer_builder_args: typer_builder.TyperBuilderArgs = {"command": command}

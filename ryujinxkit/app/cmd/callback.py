"""Callback definition for app typer."""

import enum
import importlib.metadata
import io
import json
import tarfile
import typing

import requests
import rich
import rich.progress
import rich.status
import typer

from ...core.fs.resolver import Node, resolver
from ...core.ui.objects import console
from ...core.ui.theme import ui_applier
from ...helpers.AP_decomp import Presenter, PrimitiveSignal, merge
from ..context.behavioural_control import settings
from .typer import app_typer


class _InstallSignal(int, enum.Enum):
    SERVICE_CONNECT = 0
    FAILED = 1
    DOWNLOADING = 2
    UNPACKING = 3


@app_typer.callback()
def callback(
    url: typing.Annotated[
        str | None,
        typer.Option(
            metavar="URL",
            help="Download URL (aquired from an authority).",
            envvar="RYUJINXKIT_SERVICE",
        ),
    ] = None,
    version: typing.Annotated[
        bool, typer.Option("--version", help="Show version and quit.")
    ] = False,
    json: typing.Annotated[
        bool, typer.Option("--json", help="Enable JSON output.")
    ] = settings["json"],
):
    settings["json"] = json

    if version:
        console.print(
            "[italic][colour.primary][bold]RyujinxKit[/bold][/colour.primary][/italic] "
            f"--- version {importlib.metadata.version("ryujinxkit")}"
        )

        raise typer.Exit

    if url:
        merge(_action_dispensor, _presenter())(url)

        raise typer.Exit


def _presenter() -> Presenter[tuple[_InstallSignal, float]]:
    tracking = False
    animation: rich.progress.Progress | rich.status.Status | None = None
    task_id: rich.progress.TaskID | None = None

    while True:
        match (yield):
            case _InstallSignal.SERVICE_CONNECT, _:
                animation = ui_applier(rich.status.Status)(
                    "Connecting to service..."
                )

                animation.start()

            case _InstallSignal.FAILED, 0:
                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    console.print_json(
                        data={"code": "SERVICE_CONNECTION_ISSUE"}
                    )

                    continue

                console.print("[error]Failed to connect to service.")

            case _InstallSignal.DOWNLOADING, volume:
                if tracking:
                    typing.cast(rich.progress.Progress, animation).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                typing.cast(rich.status.Status, animation).stop()

                animation = ui_applier(rich.progress.Progress)(
                    ui_applier(rich.progress.SpinnerColumn)(),
                    "{task.description}",
                    "({task.percentage:.1f}%)",
                )
                task_id = animation.add_task(
                    description="Downloading Ryujinx...", total=volume
                )
                tracking = True

                animation.start()

            case _InstallSignal.UNPACKING, volume:
                typing.cast(rich.progress.Progress, animation).stop()

                tracking = False
                animation = ui_applier(rich.status.Status)(
                    "Unpacking contents..."
                )

                animation.start()

            case _InstallSignal.FAILED, 1:
                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    console.print_json(data={"code": "NETWORK_ISSUE"})

                    continue

                console.print(
                    "An error occured. This was the resullt of one of the "
                    "following:\n",
                    "(1) Your URL locates an invalid service,",
                    "(2) Your connection timed out.",
                    "\nIn case of (1), contact an authority for a valid URL.",
                    sep="\n",
                )

            case PrimitiveSignal.FINISHED:
                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    console.print_json(
                        data={
                            "code": "SUCCESS",
                            "path": str(resolver[Node.RYUJINX_LOCAL_DATA]),
                        }
                    )

                    continue

                console.print(
                    f"Ryujinx installed to {
                        resolver[Node.RYUJINX_LOCAL_DATA]
                    }."
                )

            case PrimitiveSignal.KILL:
                if animation is not None:
                    animation.stop()

            case _:
                pass


def _action_dispensor(url: str):
    """
    :param url: Ryujinx source url.
    """

    routes = {
        "app": Node.RYUJINX_LOCAL_DATA,
        "registered": Node.RYUJINX_REGISTERED,
        "keys": Node.RYUJINX_SYSTEM,
    }

    with io.BytesIO() as buffer:
        yield (_InstallSignal.SERVICE_CONNECT, 0)

        response: requests.Response | None = None

        try:
            response = requests.get(url=url, stream=True)

            if response.status_code != 200:
                yield (_InstallSignal.FAILED, 0)
                yield PrimitiveSignal.KILL

        except requests.RequestException:
            yield (_InstallSignal.FAILED, 0)
            yield PrimitiveSignal.KILL

        response = typing.cast(requests.Response, response)

        yield (
            _InstallSignal.DOWNLOADING,
            float(response.headers.get("content-length", 0)),
        )

        try:
            for chunk in response.iter_content(pow(2, 15)):
                yield (_InstallSignal.DOWNLOADING, buffer.write(chunk))

            buffer.seek(0)

            yield (_InstallSignal.UNPACKING, 0)

            with tarfile.TarFile(fileobj=buffer) as tar:
                with typing.cast(
                    tarfile.ExFileObject, tar.extractfile("ryujinx.json")
                ) as meta:
                    leaf = "{version}-{system}".format(**json.load(meta))

                with resolver.cache_locked(
                    (Node.RYUJINX_LOCAL_DATA, f"Ryujinx/{leaf}")
                ):
                    for member in tar:
                        if member.isdir():
                            continue

                        head, *tail = member.name.split(sep="/", maxsplit=1)

                        if head not in routes:
                            continue

                        path = resolver[routes[head]] / tail[0]

                        path.parent.mkdir(parents=True, exist_ok=True)

                        with typing.cast(
                            tarfile.ExFileObject, tar.extractfile(member)
                        ) as file_buffer:
                            path.write_bytes(file_buffer.read())

        except Exception:
            yield (_InstallSignal.FAILED, 1)
            yield PrimitiveSignal.KILL

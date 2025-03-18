"""Install command.

Exports
-------
- :func:`install_command`: The install command.
"""

import collections
import collections.abc
import enum
import io
import json
import tarfile
import typing

import requests
import rich
import rich.progress
import rich.status

from ....core.fs.resolver import Node, resolver
from ....core.ui.configs import UI_CONFIGS
from ....core.ui.objects import console
from ...context import settings
from ..AP_decomp import PrimitiveSignal, merger


class InstallSignal(int, enum.Enum):
    SERVICE_CONNECT = 0
    FAILED = 1
    DOWNLOADING = 2
    UNPACKING = 3


def presenter() -> (
    collections.abc.Generator[
        None, tuple[InstallSignal, float] | PrimitiveSignal
    ]
):
    looping = False
    animation: rich.progress.Progress | rich.status.Status | None = None
    task_id: rich.progress.TaskID | None = None

    while True:
        match (yield):
            case InstallSignal.SERVICE_CONNECT, _:
                animation = console.status(
                    status="[dim]Connecting to service", spinner_style="dim"
                )

                animation.start()

            case InstallSignal.FAILED, 0:
                looping = False

                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={"code": "SERVICE_CONNECTION_ISSUE"}
                    )

                return console.print("Failed to connect to service.")

            case InstallSignal.DOWNLOADING, volume:
                if looping:
                    typing.cast(rich.progress.Progress, animation).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                typing.cast(rich.status.Status, animation).stop()

                animation = rich.progress.Progress(
                    rich.progress.SpinnerColumn(style="dim"),
                    "[dim]{task.description}",
                    "[dim]({task.percentage:.1f}%)",
                    console=console,
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
                    transient=True,
                )
                task_id = animation.add_task(
                    description="Downloading", total=volume
                )
                looping = True

                animation.start()

            case InstallSignal.UNPACKING, volume:
                typing.cast(rich.progress.Progress, animation).stop()

                looping = False
                animation = console.status(
                    status="[dim]Unpacking",
                    spinner_style="dim",
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
                )

                animation.start()

            case InstallSignal.FAILED, 1:
                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    return console.print_json(data={"code": "NETWORK_ISSUE"})

                return console.print(
                    "An error occured. This was the resullt of one of the "
                    "following:\n",
                    "(1) Your URL locates an invalid service,",
                    "(2) Your connection timed out.",
                    "\nIn case of (1), contact an authority for a valid URL.",
                    sep="\n",
                )

            case PrimitiveSignal.FINISHED:
                looping = False

                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={
                            "code": "SUCCESS",
                            "path": str(resolver[Node.RYUJINX_LOCAL_DATA]),
                        }
                    )

                return console.print(
                    f"Ryujinx installed to {
                        resolver[Node.RYUJINX_LOCAL_DATA]
                    }."
                )

            case PrimitiveSignal.KILL:
                if animation is not None:
                    animation.stop()

                return

            case _:
                pass


def action(
    url: str, chunk_size: int = pow(2, 13)
) -> collections.abc.Generator[tuple[InstallSignal, float]]:
    """
    Install Ryujinx.

    :param url: RyujinxKit service url.
    :param chunk_size: Download stream's chunk size.

    :returns: Signal generator for install command.
    """

    routes = {
        "app": Node.RYUJINX_LOCAL_DATA,
        "registered": Node.RYUJINX_REGISTERED,
        "keys": Node.RYUJINX_SYSTEM,
    }

    with io.BytesIO() as buffer:
        yield (InstallSignal.SERVICE_CONNECT, 0)

        try:
            response = requests.get(url=url, stream=True)

            if response.status_code != 200:
                yield (InstallSignal.FAILED, 0)

        except requests.RequestException:
            yield (InstallSignal.FAILED, 0)

            return

        yield (
            InstallSignal.DOWNLOADING,
            float(response.headers.get("content-length", 0)),
        )

        try:
            for chunk in response.iter_content(chunk_size):
                yield (InstallSignal.DOWNLOADING, buffer.write(chunk))

            buffer.seek(0)

            yield (InstallSignal.UNPACKING, 0)

            with tarfile.TarFile(fileobj=buffer) as tar:
                with typing.cast(
                    tarfile.ExFileObject, tar.extractfile("ryujinx.json")
                ) as meta:
                    leaf = "-".join(
                        map(json.load(meta).__getitem__, ["version", "system"])
                    )

                with resolver.cache_locked(
                    (Node.RYUJINX_LOCAL_DATA, f"Ryujinx/{leaf}")
                ):
                    for member in tar:
                        if member.isdir():
                            continue

                        with typing.cast(
                            tarfile.ExFileObject, tar.extractfile(member)
                        ) as file_buffer:
                            head, *tail = member.name.split(
                                sep="/", maxsplit=1
                            )

                            if head not in routes:
                                continue

                            path = resolver[routes[head]] / tail[0]

                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_bytes(file_buffer.read())

        except Exception:
            yield (InstallSignal.FAILED, 1)


@merger(action=action, presenter=presenter)
def install_command(
    in_: collections.abc.Generator[tuple[InstallSignal, float]],
    pole: collections.abc.Generator[
        None, tuple[InstallSignal, float] | PrimitiveSignal
    ],
) -> None:
    for message in in_:
        pole.send(message)

        if message[0] == InstallSignal.FAILED:
            return

    pole.send(PrimitiveSignal.FINISHED)

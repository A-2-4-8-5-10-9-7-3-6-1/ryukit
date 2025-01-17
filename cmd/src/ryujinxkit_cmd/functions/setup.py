"""
Ryujinx setup-functions.

Dependency level: 2.
"""

from asyncio import gather, run
from base64 import b64decode
from io import BytesIO
from json import dumps, load, loads
from pathlib import Path
from shutil import rmtree
from tarfile import TarFile
from typing import Any, Generator, Mapping

from anyio.to_thread import run_sync
from requests import HTTPError, get
from rich.progress import Progress

from ..constants.configs import (
    SETUP_CHUNK_SIZE,
    SETUP_CONNECTION_ERROR_MESSAGE,
)
from ..enums import FileNode
from ..session import Session

# =============================================================================


def _extract_tar(
    tar_bytes: bytes,
    path: Path,
) -> Generator[int, None, None]:
    """
    Extracts contents from tar file, and informs on progression.

    **Notes**:
        - Generator's first term is the task's *size*.
        - Generator's successive terms are task's chunk-sizes.

    :param tar_bytes: Contents of tar file as bytes.
    :param path: Extraction path of tar file.

    :returns: Generator for task-progression information.
    """

    with (
        BytesIO(initial_bytes=tar_bytes) as buffer,
        TarFile(fileobj=buffer) as tar,
    ):
        members = tar.getmembers()

        yield sum(member.size for member in members)

        for member in members:
            tar.extract(member=member, path=path)

            yield member.size


# -----------------------------------------------------------------------------


def _process_app_data(
    app_files: bytes,
    meta_data: bytes,
) -> Generator[int, None, None]:
    """
    Handles setup of Ryujinx app directory and path.

    **Notes**:
        - Generator's first term is the task's *size*.
        - Generator's successive terms are task's chunk-sizes.

    :param app_files: Sourced data corresponding to Ryujinx app-files.
    :param meta_data: Sourced data corresponding to Ryujinx app-meta.

    :returns: A generator for tracking task progression.
    """

    meta: Mapping[str, Any] = loads(s=meta_data)

    with Session.RESOLVER.cache_only(
        (
            FileNode.RYUJINX_APP,
            "-".join(map(meta.__getitem__, ("name", "version", "system"))),
        )
    ):
        if Session.RESOLVER(id_=FileNode.RYUJINX_APP).exists():
            rmtree(path=Session.RESOLVER(id_=FileNode.RYUJINX_APP))

        Session.RESOLVER(id_=FileNode.RYUJINX_APP).mkdir(
            parents=True, exist_ok=True
        )

        slack = Session.RESOLVER(id_=FileNode.APP_STATE).write_text(
            data=dumps(
                {
                    "app-path": Session.RESOLVER(
                        id_=FileNode.RYUJINX_APP
                    ).as_uri()
                }
            )
        )
        iterable = iter(
            _extract_tar(
                tar_bytes=app_files,
                path=Session.RESOLVER(id_=FileNode.RYUJINX_APP),
            )
        )

        yield next(iterable) + slack
        yield slack

        for size in iterable:
            yield size


# -----------------------------------------------------------------------------


async def _consume_sourced(
    sourced: Mapping[str, Any],
    progress: Progress,
) -> None:
    """
    Processes--asynchronously--data sourced from server.

    :param sourced: Data sourced from server.
    :param progress: Progress object for progression display.
    """

    jobs: list[tuple[str, Generator[int, None, None]]] = [
        (
            "App Files",
            _process_app_data(
                app_files=sourced["app-files"],
                meta_data=sourced["meta-file"],
            ),
        ),
        (
            "System Keys",
            _extract_tar(
                tar_bytes=sourced["system-keys"],
                path=Session.RESOLVER(id_=FileNode.RYUJINX_SYSTEM),
            ),
        ),
        (
            "System Registered",
            _extract_tar(
                tar_bytes=sourced["system-registered"],
                path=Session.RESOLVER(id_=FileNode.RYUJINX_REGISTERED),
            ),
        ),
    ]
    unpack_task_id = progress.add_task(
        description="[yellow]Unpacking[/yellow]",
        total=len(jobs),
    )

    await gather(
        *(
            (
                lambda task=task, iterable=job: run_sync(
                    lambda total: (
                        lambda id_=progress.add_task(
                            description=f"[dim]Unpacking: {task}[/dim]",
                            total=total,
                        ): [
                            [
                                [
                                    progress.update(task_id=id_, advance=size),
                                    progress.update(
                                        task_id=unpack_task_id,
                                        advance=size / total,
                                    ),
                                ]
                                for size in iterable
                            ],
                            progress.update(task_id=id_, visible=False),
                        ]
                    )(),
                    next(iterable),
                )
            )()
            for task, job in jobs
        )
    )


# -----------------------------------------------------------------------------


def source(server_url: str) -> None:
    """
    Source setup data from server.

    :param server_url: The server's url.
    """

    response = get(url=server_url, stream=True)

    if response.status_code != 200:
        raise HTTPError(SETUP_CONNECTION_ERROR_MESSAGE, response=response)

    with BytesIO() as buffer, Progress(transient=True) as progress:
        download_task_id = progress.add_task(
            description="[yellow]Downloading[/yellow]",
            total=float(response.headers.get("content-length", 0)),
        )

        [
            [
                buffer.write(chunk),
                progress.update(task_id=download_task_id, advance=len(chunk)),
            ]
            for chunk in response.iter_content(chunk_size=SETUP_CHUNK_SIZE)
        ]

        progress.update(
            task_id=download_task_id,
            description="[green]Downloaded[/green]",
        )

        buffer.seek(0)

        run(
            main=_consume_sourced(
                sourced={
                    packet["usage"]: b64decode(s=packet["data"])
                    for packet in load(fp=buffer)
                },
                progress=progress,
            )
        )


# =============================================================================

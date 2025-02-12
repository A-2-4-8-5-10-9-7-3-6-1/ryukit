"""
- dependency level 0.
"""

from io import BytesIO
from json import load
from tarfile import TarFile

from platformdirs import PlatformDirs
from requests import HTTPError, get
from rich.console import Console
from rich.progress import Progress, SpinnerColumn

from ryujinxkit.general import (
    RYUJINX_AUTHOR,
    SOURCE_APP,
    SOURCE_KEYS,
    SOURCE_META,
    SOURCE_REGISTERED,
    UI_REFRESH_RATE,
    FileNode,
    Session,
)

# =============================================================================


def source(console: Console, url: str, chunk_size: int = pow(2, 13)) -> None:
    """
    Source setup data.

    :param url: RyujinxKit service url.
    :param console: A console for documenting progress.
    :param chunk_size: Download-stream chunk size.

    :raises: `HTTPError` if request status code is not 200.
    """

    routes = {
        SOURCE_APP: FileNode.RYUJINX_LOCAL_DATA,
        SOURCE_REGISTERED: FileNode.RYUJINX_REGISTERED,
        SOURCE_KEYS: FileNode.RYUJINX_SYSTEM,
    }

    with BytesIO() as buffer:
        with console.status(
            status="[dim]Connecting to service",
            spinner_style="dim",
            refresh_per_second=UI_REFRESH_RATE,
        ):
            response = get(url=url, stream=True)

        if response.status_code != 200:
            raise HTTPError

        with Progress(
            SpinnerColumn(style="dim"),
            "[dim]{task.description}",
            "[dim]({task.percentage:.1f}%)",
            console=console,
            refresh_per_second=UI_REFRESH_RATE,
            transient=True,
        ) as progress:
            task_id = progress.add_task(
                description="Downloading resources",
                total=float(response.headers.get("content-length", 0)),
                modifiers="[dim]",
            )

            [
                [
                    buffer.write(chunk),
                    progress.advance(task_id=task_id, advance=chunk_size),
                ]
                for chunk in response.iter_content(chunk_size=chunk_size)
            ]

        buffer.seek(0)

        with (
            console.status(
                status="[dim]Organizing assets",
                spinner_style="dim",
                refresh_per_second=UI_REFRESH_RATE,
            ),
            TarFile(fileobj=buffer) as tar,
        ):
            ryujinx_version: str

            with tar.extractfile(member=SOURCE_META) as meta:
                ryujinx_version = str(
                    PlatformDirs(
                        appname="Ryujinx",
                        appauthor=RYUJINX_AUTHOR,
                        version="-".join(
                            map(
                                load(fp=meta).__getitem__,
                                ("version", "system"),
                            )
                        ),
                    ).user_data_path
                )

            with Session.resolver.cache_only(
                (FileNode.RYUJINX_LOCAL_DATA, ryujinx_version)
            ):
                for member in tar:
                    if member.isdir():
                        continue

                    with tar.extractfile(member=member) as file_buffer:
                        head, *tail = member.name.split(sep="/", maxsplit=1)

                        if head not in routes:
                            continue

                        path = Session.resolver(id_=routes[head]) / tail[0]

                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(file_buffer.read())


# =============================================================================

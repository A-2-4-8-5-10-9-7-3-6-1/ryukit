"""
- dependency level 0.
"""

from io import BytesIO
from json import load
from tarfile import TarFile

from platformdirs import PlatformDirs
from requests import HTTPError, get
from rich.progress import Progress

from ...general import (
    SOURCE_APP,
    SOURCE_CHUNK_SIZE,
    SOURCE_KEYS,
    SOURCE_META,
    SOURCE_REGISTERED,
    FileNode,
    Session,
)
from ...general.constants.configs import RYUJINX_AUTHOR, RYUJINX_NAME

# =============================================================================


def source(url: str) -> None:
    """
    Source setup data.

    :param url: RyujinxKit-content download url.
    """

    response = get(url=url, stream=True)

    if response.status_code != 200:
        raise HTTPError("Couldn't connect to server.", response=response)

    with Progress(transient=True) as progress, BytesIO() as buffer:
        task_id = progress.add_task(
            description="[yellow]Downloading[/yellow]",
            total=float(response.headers.get("content-length", 0)),
        )

        [
            [
                buffer.write(chunk),
                progress.update(task_id=task_id, advance=len(chunk)),
            ]
            for chunk in response.iter_content(chunk_size=SOURCE_CHUNK_SIZE)
        ]

        progress.update(
            task_id=task_id,
            description="[green]Downloaded[/green]",
        )

        buffer.seek(0)

        with TarFile(fileobj=buffer) as tar:
            task_id = progress.add_task(
                description="[yellow]Unpacking[/yellow]",
                total=sum(1 for _ in tar),
            )
            routes: dict[str, FileNode] = {
                SOURCE_APP: FileNode.RYUJINX_LOCAL_DATA,
                SOURCE_REGISTERED: FileNode.RYUJINX_REGISTERED,
                SOURCE_KEYS: FileNode.RYUJINX_SYSTEM,
            }

            with (
                tar.extractfile(member=SOURCE_META) as meta,
                Session.RESOLVER.cache_only(
                    (
                        FileNode.RYUJINX_LOCAL_DATA,
                        str(
                            PlatformDirs(
                                appname=RYUJINX_NAME,
                                appauthor=RYUJINX_AUTHOR,
                                version="-".join(
                                    map(
                                        load(fp=meta).__getitem__,
                                        ("version", "system"),
                                    )
                                ),
                            ).user_data_path
                        ),
                    )
                ),
            ):
                [
                    [
                        (
                            (
                                lambda buffer, head, tail=None: [
                                    (
                                        (
                                            lambda path: [
                                                path.parent.mkdir(
                                                    parents=True,
                                                    exist_ok=True,
                                                ),
                                                path.write_bytes(
                                                    buffer.read()
                                                ),
                                            ]
                                        )(
                                            Session.RESOLVER(id_=routes[head])
                                            / tail
                                        )
                                        if head in routes
                                        else None
                                    ),
                                    buffer.close(),
                                ]
                            )(
                                tar.extractfile(member=member),
                                *member.name.split(sep="/", maxsplit=1),
                            )
                            if not member.isdir()
                            else None
                        ),
                        progress.advance(task_id=task_id, advance=1),
                    ]
                    for member in tar
                ]


# =============================================================================

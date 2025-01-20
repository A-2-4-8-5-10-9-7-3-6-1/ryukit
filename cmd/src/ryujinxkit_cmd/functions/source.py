"""
Ryujinx setup-functions.

Dependency level: 2.
"""

from io import BytesIO
from json import load
from shutil import rmtree
from tarfile import TarFile

from requests import HTTPError, get
from rich.progress import Progress

from ..constants.configs import (
    SETUP_CHUNK_SIZE,
    SETUP_CONNECTION_ERROR_MESSAGE,
    SOURCE_APP,
    SOURCE_KEYS,
    SOURCE_META,
    SOURCE_REGISTERED,
)
from ..enums import FileNode
from ..session import Session

# =============================================================================


def source(server_url: str) -> None:
    """
    Source setup data from server.

    :param server_url: The server's url.
    """

    response = get(url=server_url, stream=True)

    if response.status_code != 200:
        raise HTTPError(SETUP_CONNECTION_ERROR_MESSAGE, response=response)

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
            for chunk in response.iter_content(chunk_size=SETUP_CHUNK_SIZE)
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
                SOURCE_APP: FileNode.RYUJINX_APP,
                SOURCE_REGISTERED: FileNode.RYUJINX_REGISTERED,
                SOURCE_KEYS: FileNode.RYUJINX_SYSTEM,
            }

            with (
                tar.extractfile(member=SOURCE_META) as buffer,
                Session.RESOLVER.cache_only(
                    (
                        FileNode.RYUJINX_APP,
                        "-".join(
                            map(
                                load(fp=buffer).__getitem__,
                                ("name", "version", "system"),
                            )
                        ),
                    )
                ),
            ):
                if Session.RESOLVER(id_=FileNode.RYUJINX_APP).exists():
                    rmtree(path=Session.RESOLVER(id_=FileNode.RYUJINX_APP))

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
                                            path.write_bytes(buffer.read()),
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

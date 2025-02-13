"""
- dependency level 0.
"""

import io
import json
import tarfile

import platformdirs
import requests
import rich.console
import rich.progress

import ryujinxkit.general


def source(
    console: rich.console.Console,
    url: str,
    chunk_size: int = pow(2, 13),
) -> None:
    """
    Source setup data.

    :param url: RyujinxKit service url.
    :param console: A console for documenting progress.
    :param chunk_size: Download-stream chunk size.

    :raises: `requests.HTTPError` if request status code is not 200.
    """

    routes = {
        ryujinxkit.general.SOURCE_APP: ryujinxkit.general.FileNode.RYUJINX_LOCAL_DATA,
        ryujinxkit.general.SOURCE_REGISTERED: ryujinxkit.general.FileNode.RYUJINX_REGISTERED,
        ryujinxkit.general.SOURCE_KEYS: ryujinxkit.general.FileNode.RYUJINX_SYSTEM,
    }

    with io.BytesIO() as buffer:
        with console.status(
            status="[dim]Connecting to service",
            spinner_style="dim",
            refresh_per_second=ryujinxkit.general.UI_REFRESH_RATE,
        ):
            response = requests.get(url=url, stream=True)

        if response.status_code != 200:
            raise requests.HTTPError

        with rich.progress.Progress(
            rich.progress.SpinnerColumn(style="dim"),
            "[dim]{task.description}",
            "[dim]({task.percentage:.1f}%)",
            console=console,
            refresh_per_second=ryujinxkit.general.UI_REFRESH_RATE,
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
                refresh_per_second=ryujinxkit.general.UI_REFRESH_RATE,
            ),
            tarfile.TarFile(fileobj=buffer) as tar,
        ):
            ryujinx_version: str

            with tar.extractfile(
                member=ryujinxkit.general.SOURCE_META
            ) as meta:  # type: ignore
                ryujinx_version = str(
                    platformdirs.PlatformDirs(
                        appname="Ryujinx",
                        appauthor=ryujinxkit.general.RYUJINX_AUTHOR,
                        version="-".join(
                            map(
                                json.load(fp=meta).__getitem__,
                                ("version", "system"),
                            )
                        ),
                    ).user_data_path
                )

            with ryujinxkit.general.Session.resolver.cache_locked(
                (
                    ryujinxkit.general.FileNode.RYUJINX_LOCAL_DATA,
                    ryujinx_version,
                )
            ):
                for member in tar:
                    if member.isdir():
                        continue

                    with tar.extractfile(member=member) as file_buffer:  # type: ignore
                        head, *tail = member.name.split(sep="/", maxsplit=1)

                        if head not in routes:
                            continue

                        path = (
                            ryujinxkit.general.Session.resolver(
                                id_=routes[head]
                            )
                            / tail[0]
                        )

                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(file_buffer.read())

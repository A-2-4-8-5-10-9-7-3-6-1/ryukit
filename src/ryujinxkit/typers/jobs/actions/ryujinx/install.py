"""
- dependency level 2.
"""

import collections.abc
import io
import json
import tarfile

import platformdirs
import requests

from .....file_access.resolver import resolver
from .....file_access.resolver_node import ResolverNode


def action(
    url: str,
    chunk_size: int = pow(2, 13),
) -> collections.abc.Generator[tuple[str, float]]:
    """
    Install Ryujinx.

    :param url: RyujinxKit service url.
    :param chunk_size: Download stream's chunk size.
    """

    routes = {
        "app": ResolverNode.RYUJINX_LOCAL_DATA,
        "registered": ResolverNode.RYUJINX_REGISTERED,
        "keys": ResolverNode.RYUJINX_SYSTEM,
    }

    with io.BytesIO() as buffer:
        yield ("SERVICE_CONNECT", 0)

        response = requests.get(url=url, stream=True)

        if response.status_code != 200:
            yield ("DOWNLOADING", -1)

        yield ("DOWNLOADING", float(response.headers.get("content-length", 0)))

        for chunk in response.iter_content(chunk_size=chunk_size):
            yield ("DOWNLOADING", buffer.write(chunk))

        buffer.seek(0)

        yield ("UNPCKING", 0)

        try:
            with tarfile.TarFile(fileobj=buffer) as tar:
                ryujinx_local: str

                with tar.extractfile(member="ryujinx.json") as meta:  # type: ignore
                    ryujinx_local = str(
                        platformdirs.PlatformDirs(
                            appname="Ryujinx",
                            appauthor=False,
                            version="-".join(
                                map(
                                    json.load(fp=meta).__getitem__,
                                    ["version", "system"],
                                )
                            ),
                        ).user_data_path
                    )

                with resolver.cache_locked(
                    (
                        ResolverNode.RYUJINX_LOCAL_DATA,
                        ryujinx_local,
                    )
                ):
                    for member in tar:
                        if member.isdir():
                            continue

                        with tar.extractfile(member=member) as file_buffer:  # type: ignore
                            head, *tail = member.name.split(
                                sep="/", maxsplit=1
                            )

                            if head not in routes:
                                continue

                            path = resolver[routes[head]] / tail[0]

                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_bytes(file_buffer.read())

        except Exception:
            yield ("UNPACKING", -1)

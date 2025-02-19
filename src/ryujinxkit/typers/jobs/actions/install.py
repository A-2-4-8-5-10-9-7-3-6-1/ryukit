import collections.abc
import io
import json
import tarfile

import requests

from ....file_access.resolver import resolver
from ....file_access.resolver_node import ResolverNode


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
            yield ("FAILED", 0)

        yield ("DOWNLOADING", float(response.headers.get("content-length", 0)))

        try:
            for chunk in response.iter_content(chunk_size=chunk_size):
                yield ("DOWNLOADING", buffer.write(chunk))

            buffer.seek(0)

            yield ("UNPCKING", 0)

            with tarfile.TarFile(fileobj=buffer) as tar:
                ryujinx_leaf: str

                with tar.extractfile(member="ryujinx.json") as meta:  # type: ignore
                    ryujinx_leaf = "-".join(
                        map(
                            json.load(fp=meta).__getitem__,
                            ["version", "system"],
                        )
                    )

                with resolver.cache_locked(
                    (
                        ResolverNode.RYUJINX_LOCAL_DATA,
                        f"Ryujinx/{ryujinx_leaf}",
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
            yield ("FAILED", 1)

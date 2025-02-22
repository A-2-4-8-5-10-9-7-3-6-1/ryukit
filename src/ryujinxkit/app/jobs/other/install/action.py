import collections.abc
import io
import json
import tarfile
import typing

import requests

from .....libs.fs.node import Node
from .....libs.fs.resolver import resolver
from .signals import InstallSignal


def action(
    url: str,
    chunk_size: int = pow(2, 13),
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

        response = requests.get(url=url, stream=True)

        if response.status_code != 200:
            yield (InstallSignal.FAILED, 0)

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
                    tarfile.ExFileObject,
                    tar.extractfile("ryujinx.json"),
                ) as meta:
                    leaf = "-".join(
                        map(
                            json.load(meta).__getitem__,
                            ["version", "system"],
                        )
                    )

                with resolver.cache_locked(
                    (Node.RYUJINX_LOCAL_DATA, f"Ryujinx/{leaf}")
                ):
                    for member in tar:
                        if member.isdir():
                            continue

                        with typing.cast(
                            tarfile.ExFileObject,
                            tar.extractfile(member),
                        ) as file_buffer:
                            head, *tail = member.name.split(
                                sep="/",
                                maxsplit=1,
                            )

                            if head not in routes:
                                continue

                            path = resolver[routes[head]] / tail[0]

                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_bytes(file_buffer.read())

        except Exception:
            yield (InstallSignal.FAILED, 1)

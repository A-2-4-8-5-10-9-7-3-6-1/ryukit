"""Implementations for common command logic."""

import collections
import collections.abc
import pathlib
import shutil
import typing

from ..core import fs, runtime


def channel_save_bucket(bucket_id: int, *, upstream: bool):
    """
    Channel content between a save bucket and Ryujinx.

    :param upstream: Set as true to channel from the bucket to Ryujinx, and as false to do the reverse.
    :param bucket_id: ID belonging to the subject save bucket.

    :raises RuntimeError: If Ryujinx is not installed.
    """

    rotate: collections.abc.Callable[
        [collections.abc.Sequence[str]], collections.abc.Iterable[str]
    ] = ((lambda x: x) if upstream else reversed[str])
    ryujinxInfo = typing.cast(
        dict[str, object], runtime.context.persistence_layer["ryujinx"]
    )

    if not ryujinxInfo["meta"]:
        raise RuntimeError("Couldn't detect Ryujinx.")

    for source, dest in map(
        lambda pair: (
            fs.File.SAVE_INSTANCE_FOLDER(instance_id=bucket_id) / next(pair),
            pathlib.Path(
                next(pair).format(
                    **typing.cast(dict[str, object], ryujinxInfo["meta"]),
                    **typing.cast(
                        dict[str, object],
                        runtime.context.configs["ryujinxConfigs"],
                    ),
                )
            ),
        ),
        map(
            iter,
            map(
                rotate,
                typing.cast(
                    dict[str, str],
                    typing.cast(
                        dict[str, object],
                        runtime.context.internal_layer["saveBuckets"],
                    )["flow"],
                ).items(),
            ),
        ),
    ):
        if dest.exists():
            shutil.rmtree(dest)

        if not source.exists():
            continue

        shutil.copy(source, dest)

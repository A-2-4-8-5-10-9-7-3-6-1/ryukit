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

    def rotate[T](values: collections.abc.Sequence[T]):
        return (iter if upstream else reversed)(values)

    ryujinxInfo = typing.cast(
        dict[str, object], runtime.context.persistence_layer["ryujinx"]
    )

    if not ryujinxInfo["meta"]:
        raise RuntimeError("Couldn't detect Ryujinx.")

    ryujinxInfo["meta"] = typing.cast(dict[str, object], ryujinxInfo["meta"])
    ryujinxInfo["ryujinxConfigs"] = typing.cast(
        dict[str, object], runtime.context.configs["ryujinxConfigs"]
    )

    for source, dest in map(
        rotate,
        map(
            lambda x: list(map(pathlib.Path, x)),
            map(
                lambda pair, r_conf=ryujinxInfo[
                    "ryujinxConfigs"
                ], meta=ryujinxInfo["meta"]: (
                    str(
                        fs.File.SAVE_INSTANCE_FOLDER(instance_id=bucket_id)
                        / pair[0]
                    )
                    .format(**r_conf)
                    .format(**meta),
                    pair[1].format(**r_conf).format(**meta),
                ),
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

        shutil.copytree(source, dest)

"""Implementations for common command logic."""

import collections
import collections.abc
import json
import pathlib
import shutil
import typing

from ..core import fs, state


def channel_save_bucket(bucket_id: int, *, upstream: bool):
    """
    Channel content between a save bucket and Ryujinx.

    :param upstream: True to channel from the bucket to Ryujinx, False to do the reverse.
    :param bucket_id: ID belonging to the subject save bucket.

    :raises RuntimeError: If Ryujinx is not installed.
    """

    orientate: collections.abc.Callable[
        [collections.abc.Sequence[str]], collections.abc.Iterable[str]
    ] = ((lambda x: x) if upstream else reversed[str])
    ryujinxMeta = typing.cast(
        dict[str, object] | None,
        typing.cast(
            dict[str, object],
            json.loads(fs.File.STATE_FILE().read_bytes())["ryujinx"],
        ).get("meta"),
    )

    if not ryujinxMeta:
        raise RuntimeError("Couldn't detect Ryujinx.")

    for source, dest in map(
        lambda pair: (
            fs.File.SAVE_INSTANCE_FOLDER(instance_id=bucket_id) / next(pair),
            pathlib.Path(
                next(pair).format(
                    **ryujinxMeta,
                    **typing.cast(
                        dict[str, object],
                        state.states.configs["ryujinxConfigs"],
                    ),
                )
            ),
        ),
        map(
            iter,
            map(
                orientate,
                typing.cast(
                    dict[str, str],
                    typing.cast(
                        dict[str, object],
                        state.internal_configs["saveBuckets"],
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

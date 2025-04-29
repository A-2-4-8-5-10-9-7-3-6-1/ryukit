import collections
import collections.abc
import pathlib
import shutil
import typing

import typer

from ...core import db
from ...core.fs import File
from ..__context__ import *
from .__context__ import *

__all__ = ["save", "channel_save_bucket", "save_bucket_exists"]
save = typer.Typer(name="save")
app.add_typer(save)


@save.callback()
def _():
    "Manage your save buckets."


def channel_save_bucket(bucket_id: int, *, upstream: bool):
    """
    Channel content between a save bucket and Ryujinx.

    :param upstream: Set as true to channel from the bucket to Ryujinx, and as false to do the reverse.
    :param bucket_id: ID belonging to the subject save bucket.
    :raises RuntimeError: If Ryujinx is not installed.
    """

    def rotate[T](values: collections.abc.Sequence[T]):
        return (iter if upstream else reversed)(values)

    ryujinx_info = typing.cast(
        dict[str, object], intersession_state["ryujinx"]
    )
    if not ryujinx_info["meta"]:
        raise RuntimeError("Couldn't locate Ryujinx.")
    ryujinx_info["meta"] = typing.cast(dict[str, object], ryujinx_info["meta"])
    ryujinx_info["ryujinxConfigs"] = typing.cast(
        dict[str, object], configs["ryujinxConfigs"]
    )
    for source, dest in map(
        rotate,
        map(
            lambda x: list(map(pathlib.Path, x)),
            map(
                lambda pair, ryujinx_config=ryujinx_info[
                    "ryujinxConfigs"
                ], meta=ryujinx_info["meta"]: (
                    str(
                        File.SAVE_INSTANCE_FOLDER(instance_id=bucket_id)
                        / pair[0]
                    )
                    .format(**ryujinx_config)
                    .format(**meta),
                    pair[1].format(**ryujinx_config).format(**meta),
                ),
                typing.cast(
                    dict[str, str],
                    typing.cast(dict[str, object], system["saveBuckets"])[
                        "flow"
                    ],
                ).items(),
            ),
        ),
    ):
        if dest.exists():
            shutil.rmtree(dest)
        if not source.exists():
            continue
        shutil.copytree(source, dest)


def save_bucket_exists(id_: int):
    """
    Check whether or not a save bucket exists.

    :param id_: The save bucket's ID.
    """

    with db.connect() as conn:
        return (
            conn.execute(
                """
                SELECT
                    COUNT(*)
                FROM
                    ryujinx_saves
                WHERE
                    id = :id;
                """,
                {"id": id_},
            ).fetchone()[0]
            != 0
        )

import filecmp
import importlib
import importlib.resources
import multiprocessing
import os
import pathlib
import random
import shutil
import signal
import tarfile
import tempfile
import time
from typing import Literal, cast

import setproctitle
import sqlalchemy
import typer
from pytest import mark

from ryukit import utils as ryutils
from ryukit.app.__context__ import USER_CONFIGS
from ryukit.app.install_ryujinx import install_ryujinx
from ryukit.app.save.__context__ import channel_save_bucket
from ryukit.app.save.apply import apply
from ryukit.app.save.create import create
from ryukit.app.save.drop import drop
from ryukit.app.save.dump import dump
from ryukit.app.save.ls import ls
from ryukit.app.save.pull import pull
from ryukit.app.save.relabel import relabel
from ryukit.app.save.restore import restore
from ryukit.app.track import track
from ryukit.libs import db, paths

from . import utils

__all__ = [
    "test_install_ryujinx",
    "test_save_create",
    "test_save_drop",
    "test_save_ls",
    "test_save_apply",
    "test_save_dump",
    "test_save_restore",
    "test_track",
]


# NOTE: Coverage doesn't work, because of child-process usage.
@mark.parametrize(
    "use, stop",
    [(None, "app"), (None, "track"), (2, "app"), (3, "track"), (2, "track")],
)
def test_track(seed: object, use: int | None, stop: Literal["app", "track"]):
    def null_process():
        setproctitle.setproctitle("Ryujinx.exe")
        while True:
            pass

    expected_size = 0
    if use is not None:
        channel_save_bucket(use, upstream=True)
        with db.client() as client:
            expected_size = cast(
                db.RyujinxSave, client.get(db.RyujinxSave, use)
            ).size
    processes = {
        "app": multiprocessing.Process(target=null_process),
        "track": multiprocessing.Process(target=track, args=[1]),
    }
    any(processes[process].start() for process in ["app", "track"])
    time.sleep(random.random())
    (
        processes[stop].terminate()
        if stop == "app"
        else os.kill(cast(int, processes[stop].pid), signal.SIGINT)
    )
    processes["track"].join()
    with db.client() as client:
        assert (
            cast(db.RyujinxSave, client.get(db.RyujinxSave, 1)).size
            == expected_size
        ), "App progress was not tracked."
    any(process.kill() for process in processes.values() if process.is_alive())


def test_save_dump(seed: object):
    with tempfile.TemporaryDirectory() as dir:
        dump_file = pathlib.Path(dir) / "dump"
        dump(dump_file)
        for part, path in [
            ("test", dump_file),
            ("truth", str(importlib.resources.files("tests") / "saves")),
        ]:
            with tarfile.open(path) as tar:
                tar.extractall(f"{dir}/{part}")
        comparison = filecmp.dircmp(f"{dir}/test", f"{dir}/truth")
        assert (
            []
            == comparison.diff_files
            == comparison.left_only
            == comparison.right_only
        ), "Invalid dump content."


def test_save_restore(seed: object):
    with tempfile.TemporaryDirectory() as dir:
        shutil.move(
            pathlib.Path(paths.SAVE_INSTANCE_DIR).parent, f"{dir}/truth"
        )
        with db.client() as client1:
            pathlib.Path(paths.DATABASE_FILE).unlink()
            restore(
                pathlib.Path(str(importlib.resources.files("tests") / "saves"))
            )
            shutil.move(
                pathlib.Path(paths.SAVE_INSTANCE_DIR).parent, f"{dir}/test"
            )
            comparison = filecmp.dircmp(f"{dir}/test", f"{dir}/truth")
            with db.client() as client2:
                assert list(
                    map(
                        ryutils.model_to_dict,
                        client2.scalars(sqlalchemy.select(db.RyujinxSave)),
                    )
                ) == list(
                    map(
                        ryutils.model_to_dict,
                        client1.scalars(sqlalchemy.select(db.RyujinxSave)),
                    )
                ) and (
                    []
                    == comparison.diff_files
                    == comparison.left_only
                    == comparison.right_only
                ), "Failed to restore content."


def test_relabel(seed: object):
    with db.client() as client:
        save = cast(db.RyujinxSave, client.get(db.RyujinxSave, 1))
        label = f"{save.label}+"
        relabel(1, as_=label)
        client.refresh(save)
        assert save.label == label, "Label did not update as expected."


@mark.parametrize("id_", [1, 2, 5])
def test_save_apply(seed: object, id_: int):
    with db.client() as client:
        save = cast(db.RyujinxSave, client.get(db.RyujinxSave, id_))
        initial_stamp = save.updated
        apply(id_)
        client.refresh(save)
        assert save.updated != initial_stamp, "Updated stamp did not change."


@mark.parametrize("push", [None, 1, 5])
def test_save_pull(seed: object, push: int | None):
    with db.client() as client:
        expected = 0
        if push is not None:
            expected = cast(
                db.RyujinxSave, client.get(db.RyujinxSave, push)
            ).size
            channel_save_bucket(push, upstream=True)
        pull(1)
        assert (
            cast(db.RyujinxSave, client.get(db.RyujinxSave, 1)).size
            == expected
        )


@utils.requires_vars("RYUKIT_INSTALL_URL")
@mark.parametrize("url", ["BAD_URL", "RYUKIT_INSTALL_URL"])
def test_install_ryujinx(url: str):
    USER_CONFIGS["ryujinxInstallURL"] = os.environ.get(url, url)
    try:
        install_ryujinx()
        assert url == "RYUKIT_INSTALL_URL", "Install passed for invalid URL."
    except typer.Exit:
        assert url != "RYUKIT_INSTALL_URL", "Install failed for valid URL."


@mark.parametrize("label", [None, "LABELLED"])
def test_save_create(seed: object, label: str | None):
    create(label) if label else create()
    with db.client() as client:
        assert (
            client.scalar(
                sqlalchemy.select(sqlalchemy.func.count()).select_from(
                    db.RyujinxSave
                )
            )
            or 0
        ) == 6, "No bucket was created."
        if label is None:
            return
        assert (
            client.scalar(
                sqlalchemy.select(sqlalchemy.func.count())
                .select_from(db.RyujinxSave)
                .where(db.RyujinxSave.label == label)
            )
            or 0
        ) >= 1


@mark.parametrize("ids", [[], [1], [1, 2, 3, 4, 5]])
def test_save_drop(seed: object, ids: list[int]):
    drop(ids)
    with db.client() as client:
        assert set(
            client.scalars(sqlalchemy.select(db.RyujinxSave.id))
        ) == set(
            i for i in range(1, 6) if i not in ids
        ), "Unexpected ID set remaining."


@mark.parametrize(
    "wildcards, filters, expected",
    [
        (
            False,
            None,
            ""
            "                                                                                \n  ID   LABEL             CREATED          UPDATED           LAST USED    SIZE   \n ────────────────────────────────────────────────────────────────────────────── \n  1    save2025052413…   2025-05-24       2025-05-24        Never       19.7MB  \n                         13:12:36         13:12:36                              \n  2    save2025052413…   2025-05-24       2025-05-24        Never       13.1MB  \n                         13:12:39         13:12:39                              \n  3    LABELLED          2025-05-24       2025-05-24        Never       0.0MB   \n                         13:13:00         13:13:00                              \n  4    save2025052413…   2025-05-24       2025-05-24        Never       0.0MB   \n                         13:13:07         13:13:07                              \n  5    RELABELLED        2025-05-24       2025-05-24        Never       6.6MB   \n                         13:13:14         13:13:41.966280                       \n                                                                                \n"
            "",
        )
    ],
)
def test_save_ls(
    seed: object, wildcards: bool, filters: list[str] | None, expected: str
):
    with ryutils.capture_out() as register:
        db.CLIENT_CONFIGS.update({"echo": False})
        ls(wildcards, filters)
    db.CLIENT_CONFIGS.update({"echo": True})
    assert register.pop() == expected, "Incorr ect format in output."

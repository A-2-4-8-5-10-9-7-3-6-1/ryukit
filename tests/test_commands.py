import filecmp
import importlib
import importlib.resources
import json
import multiprocessing
import os
import pathlib
import random
import shutil
import tarfile
import tempfile
import time
from typing import cast

import click
import psutil
import setproctitle
import sqlalchemy
from pytest import mark

from ryukit import utils as ryutils
from ryukit.app import track
from ryukit.app.__context__ import PARSERS, USER_CONFIGS
from ryukit.app.install_ryujinx import install_ryujinx
from ryukit.app.save.__context__ import HELPERS as SAVE_HELPERS
from ryukit.app.save.apply import apply
from ryukit.app.save.create import create
from ryukit.app.save.drop import drop
from ryukit.app.save.dump import dump
from ryukit.app.save.ls import ls
from ryukit.app.save.pull import pull
from ryukit.app.save.relabel import relabel
from ryukit.app.save.restore import restore
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


@mark.parametrize(
    "save_to, load_with, kill_app",
    [
        (0, None, True),
        (0, None, False),
        (0, 2, True),
        (0, 2, False),
        (0, 3, False),
    ],
)
def test_track(
    seed: object, kill_app: bool, load_with: int | None, save_to: int
):
    def null_process():
        setproctitle.setproctitle("Ryujinx.exe")
        while True:
            pass

    expected_size = 0
    if load_with is not None:
        SAVE_HELPERS["channel_save_bucket"](load_with, upstream=True)
        with db.client() as client:
            expected_size = cast(
                db.RyujinxSave, client.get(db.RyujinxSave, load_with)
            ).size
    app = multiprocessing.Process(target=null_process)
    app.start()
    track.track(save_to)
    assert pathlib.Path(
        paths.TRACKER_FILE
    ).exists(), "Did not write into tracker file."
    pid: int | None = json.loads(
        pathlib.Path(paths.TRACKER_FILE).read_bytes()
    )["pid"]
    assert pid is not None, "Couldn't read tracker's PID."
    time.sleep(random.triangular(0, 2, 0.2))
    assert psutil.pid_exists(pid), "Tracker process is not running."
    app.terminate() if kill_app else track.CALLBACKS["halt"]()
    timeout = 10
    while (
        psutil.pid_exists(pid)
        and psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
    ):
        if not timeout:
            assert (
                False
            ), "Tracker (likely) continued running after termination event."
        time.sleep(0.3)
        timeout -= 1
    with db.client() as client:
        assert (
            cast(db.RyujinxSave, client.get(db.RyujinxSave, save_to)).size
            == expected_size
        ), "App progress was not tracked."
    app.terminate()
    app.join()
    app.close()


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
        relabel(PARSERS["bucket"](1), as_=label)
        client.refresh(save)
        assert save.label == label, "Label did not update as expected."


@mark.parametrize("id_", [1, 2, 5])
def test_save_apply(seed: object, id_: int):
    with db.client() as client:
        save = cast(db.RyujinxSave, client.get(db.RyujinxSave, id_))
        initial_stamp = save.updated
        apply(PARSERS["bucket"](id_))
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
            SAVE_HELPERS["channel_save_bucket"](push, upstream=True)
        pull(PARSERS["bucket"](1))
        assert (
            cast(db.RyujinxSave, client.get(db.RyujinxSave, 1)).size
            == expected
        ), "Did not read data from Ryujinx distro."


@utils.requires_vars("RYUKIT_INSTALL_URL")
@mark.parametrize("url", ["BAD_URL", "RYUKIT_INSTALL_URL"])
def test_install_ryujinx(url: str):
    USER_CONFIGS["ryujinxInstallURL"] = os.environ.get(url, url)
    try:
        install_ryujinx()
        assert url == "RYUKIT_INSTALL_URL", "Install passed for invalid URL."
    except click.UsageError:
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
    drop(list(map(PARSERS["bucket"], ids)))
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

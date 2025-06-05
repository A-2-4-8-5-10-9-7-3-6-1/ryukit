import filecmp
import importlib
import importlib.resources
import multiprocessing
import os
import pathlib
import random
import shutil
import subprocess
import tarfile
import tempfile
import time
from typing import Literal, cast

import psutil
import setproctitle
import sqlalchemy
from pytest import mark

from ryukit.app.save.__context__ import HELPERS as SAVE_HELPERS
from ryukit.libs import db, paths
from ryukit.utils import misc as ryutils

from .. import utils

__all__ = [
    "test_install_ryujinx",
    "test_save_create",
    "test_save_drop",
    "test_save_ls",
    "test_save_apply",
    "test_save_dump",
    "test_save_restore",
    "test_track",
    "test_save_relabel",
    "test_save_pull",
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
            time.sleep(100000)

    def stop_app():
        app.terminate()
        app.join()

    expected_size = 0
    if use is not None:
        channel_save_bucket(use, upstream=True)
        with db.client() as client:
            expected_size = cast(
                db.RyujinxSave, client.get(db.RyujinxSave, use)
            ).size
    app = multiprocessing.Process(target=null_process)
    app.start()
    subprocess.run(["ryukit", "track", str(save_to)])
    pid: int | None = json.loads(
        pathlib.Path(paths.TRACKER_FILE).read_bytes()
    )["pid"]
    assert pid is not None, "Couldn't read tracker's PID."
    time.sleep(random.triangular(0, 2, 0.2))
    assert psutil.pid_exists(pid), "Tracker process is not running."
    stop_app() if kill_app else subprocess.run(["ryukit", "track", "--halt"])
    time_metrics = {"timeout": 2, "frequency": 0.1}
    while (
        psutil.pid_exists(pid)
        and psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
    ):
        if not time_metrics["timeout"]:
            raise AssertionError("Tracker was not stopped on time.")
        time.sleep(time_metrics["frequency"])
        time_metrics["timeout"] -= time_metrics["frequency"]
    with db.client() as client:
        assert (
            cast(db.RyujinxSave, client.get(db.RyujinxSave, 1)).size
            == expected_size
        ), "App progress was not saved."
    stop_app()
    app.close()


def test_save_dump(seed: object):
    with tempfile.TemporaryDirectory() as dir:
        dump_file = pathlib.Path(dir) / "dump"
        subprocess.run(["ryukit", "save", "dump", dump_file])
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
            subprocess.run(
                [
                    "ryukit",
                    "save",
                    "restore",
                    str(importlib.resources.files("tests") / "saves"),
                ]
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


def test_save_relabel(seed: object):
    with db.client() as client:
        save = cast(db.RyujinxSave, client.get(db.RyujinxSave, 1))
        label = f"{save.label}+"
        subprocess.run(["ryukit", "save", "relabel", "1", label])
        client.refresh(save)
        assert save.label == label, "Label did not update as expected."


@mark.parametrize("id_", [1, 2, 5])
def test_save_apply(seed: object, id_: int):
    with db.client() as client:
        save = cast(db.RyujinxSave, client.get(db.RyujinxSave, id_))
        initial_stamp = save.updated
        subprocess.run(["ryukit", "save", "apply", str(id_)])
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
        subprocess.run(["ryukit", "save", "pull", "1"])
        assert (
            cast(db.RyujinxSave, client.get(db.RyujinxSave, 1)).size
            == expected
        )


@utils.requires_vars("RYUKIT_INSTALL_URL")
@mark.parametrize("url", ["BAD_URL", "RYUKIT_INSTALL_URL"])
def test_install_ryujinx(url: str):
    assert (url != "RYUKIT_INSTALL_URL") == subprocess.run(
        ["ryukit", "install_ryujinx", os.environ.get(url, url)]
    ).returncode, "Install passed for invalid URL."


@mark.parametrize("label", [None, "LABELLED"])
def test_save_create(seed: object, label: str | None):
    subprocess.run(["ryukit", "save", "create", *([label] if label else [])])
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
                sqlalchemy.select(db.RyujinxSave.label, db.RyujinxSave.id)
                .order_by(db.RyujinxSave.id.desc())
                .limit(1)
            )
            == label
        )


@mark.parametrize("ids", [[1], [1, 2, 3, 4, 5], [3, 2], [5, 3, 1]])
def test_save_drop(seed: object, ids: list[str]):
    subprocess.run(["ryukit", "save", "drop", *map(str, ids)])
    with db.client() as client:
        assert set(
            client.scalars(sqlalchemy.select(db.RyujinxSave.id))
        ) == set(
            filter(lambda i: i not in ids, range(1, 6))
        ), "Unexpected ID set remaining."


@mark.parametrize(
    "wildcards, filters, expected",
    [
        (
            False,
            None,
            "                                                                                \n  ID   LABEL             CREATED          UPDATED           LAST USED    SIZE   \n ────────────────────────────────────────────────────────────────────────────── \n  1    save2025052413…   2025-05-24       2025-05-24        Never       19.7MB  \n                         13:12:36         13:12:36                              \n  2    save2025052413…   2025-05-24       2025-05-24        Never       13.1MB  \n                         13:12:39         13:12:39                              \n  3    LABELLED          2025-05-24       2025-05-24        Never       0.0MB   \n                         13:13:00         13:13:00                              \n  4    save2025052413…   2025-05-24       2025-05-24        Never       0.0MB   \n                         13:13:07         13:13:07                              \n  5    RELABELLED        2025-05-24       2025-05-24        Never       6.6MB   \n                         13:13:14         13:13:41.966280                       \n                                                                                \n",
        )
    ],
)
def test_save_ls(
    seed: object, wildcards: bool, filters: list[str] | None, expected: str
):
    options: list[str] = []
    options.append("--wildcards") if wildcards else None
    options.extend(filters or [])
    assert (
        subprocess.run(
            ["ryukit", "save", "ls", *options], capture_output=True, text=True
        ).stdout
        == expected
    ), "Incorrect format in output."

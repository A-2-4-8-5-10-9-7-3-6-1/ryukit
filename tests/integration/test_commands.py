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
from typing import cast

import psutil
import setproctitle
import sqlalchemy
from pytest import mark

from ryukit.libs import db, paths
from ryukit.utils import misc

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


def null():
    setproctitle.setproctitle("Ryujinx.exe")
    while True:
        time.sleep(10)


@mark.parametrize(
    "to, load_with, kill_app",
    [
        (0, None, True),
        (1, None, False),
        (2, 2, True),
        (3, 2, False),
        (4, 3, False),
    ],
)
def test_track(seed: object, kill_app: bool, load_with: int | None, to: int):
    def stop_app():
        app.terminate()
        app.join()

    expected_size = 0
    if load_with is not None:
        subprocess.run(["ryukit", "save", "apply", str(load_with)])
        with db.client() as client:
            expected_size = cast(
                db.RyujinxSave, client.get(db.RyujinxSave, use)
            ).size
    app = multiprocessing.Process(target=null, daemon=True)
    app.start()
    subprocess.run(["ryukit", "track", str(to)])
    pid: int | None = json.loads(
        pathlib.Path(paths.TRACKER_FILE).read_bytes()
    )["pid"]
    assert pid is not None, "Couldn't read tracker's PID."
    time.sleep(random.triangular(0, 2, 0.2))
    assert psutil.pid_exists(pid), "Tracker process is not running."
    stop_app() if kill_app else subprocess.run(["ryukit", "track", "--stop"])
    start_time = time.perf_counter()
    while (
        psutil.pid_exists(pid)
        and psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
    ):
        if time.perf_counter() - start_time > 10:
            raise AssertionError("Tracker was not stopped on time.")
        time.sleep(0.5)
    with db.client() as client:
        assert (
            abs(
                cast(db.RyujinxSave, client.get(db.RyujinxSave, to)).size
                - expected_size
            )
            < 30
        ), "App progress was not saved."
    stop_app()


def test_save_dump(seed: object):
    with tempfile.TemporaryDirectory() as dir:
        subprocess.run(["ryukit", "save", "dump", pathlib.Path(dir) / "dump"])
        for part, path in [
            ("test", pathlib.Path(dir) / "dump"),
            ("truth", str(importlib.resources.files("tests") / "saves")),
        ]:
            with tarfile.open(path) as tar:
                tar.extractall(pathlib.Path(dir) / part)
        comparison = filecmp.dircmp(
            pathlib.Path(dir) / "test", pathlib.Path(dir) / "truth"
        )
        assert (
            []
            == comparison.diff_files
            == comparison.left_only
            == comparison.right_only
        ), "Invalid dump content."


def test_save_restore(seed: object):
    with tempfile.TemporaryDirectory() as dir:
        shutil.move(
            pathlib.Path(paths.SAVE_INSTANCE_DIR).parent,
            pathlib.Path(dir) / "truth",
        )
        with db.client() as client:
            initial_saves = list(
                map(
                    misc.model_to_dict,
                    client.scalars(sqlalchemy.select(db.RyujinxSave)),
                )
            )
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
            pathlib.Path(paths.SAVE_INSTANCE_DIR).parent,
            pathlib.Path(dir) / "test",
        )
        comparison = filecmp.dircmp(
            pathlib.Path(dir) / "test", pathlib.Path(dir) / "truth"
        )
        with db.client() as client:
            assert list(
                map(
                    misc.model_to_dict,
                    client.scalars(sqlalchemy.select(db.RyujinxSave)),
                )
            ) == initial_saves and (
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
    expected = 0
    with db.client() as client:
        if push is not None:
            expected = cast(
                db.RyujinxSave, client.get(db.RyujinxSave, push)
            ).size
            subprocess.run(["ryukit", "save", "apply", str(push)])
        subprocess.run(["ryukit", "save", "pull", "1"])
        assert (
            abs(
                cast(db.RyujinxSave, client.get(db.RyujinxSave, 1)).size
                - expected
            )
            < 30
        ), "Did not read data correctly."


@utils.requires_vars("RYUKIT_INSTALL_URL")
@mark.parametrize("url", ["BAD_URL", "RYUKIT_INSTALL_URL"])
def test_install_ryujinx(url: str):
    shutil.rmtree(paths.RYUJINX_DIST_DIR, ignore_errors=True)
    assert (url == "RYUKIT_INSTALL_URL") == (
        not subprocess.run(
            ["ryukit", "install_ryujinx", os.environ.get(url, url)]
        ).returncode
        and pathlib.Path(paths.RYUJINX_DIST_DIR).exists()
    ), "Install passed for invalid URL."


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
    "wildcards, filters, expected_text",
    [(False, None, ["1", "2", "3", "4", "5"])],
)
def test_save_ls(
    seed: object,
    wildcards: bool,
    filters: list[str] | None,
    expected_text: list[int],
):
    call = ["ryukit", "save", "ls"]
    call.append("--wildcards") if wildcards else None
    call.extend(filters or [])
    result = subprocess.run(call, capture_output=True, text=True).stdout
    assert all(
        f"{text} " in result for text in expected_text
    ), "Incorrect format in output."

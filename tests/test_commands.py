import filecmp
import importlib
import importlib.resources
import os
import pathlib
import shutil
import tarfile
import tempfile
from typing import cast

import sqlalchemy
from pytest import mark

from ryukit import utils as ryutils
from ryukit.app.__context__ import USER_CONFIGS
from ryukit.app.install_ryujinx import install_ryujinx
from ryukit.app.save.apply import apply
from ryukit.app.save.create import create
from ryukit.app.save.drop import drop
from ryukit.app.save.dump import dump
from ryukit.app.save.ls import ls
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
]


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


@utils.requires_vars("RYUKIT_INSTALL_URL")
@mark.parametrize("url", ["BAD_URL", "RYUKIT_INSTALL_URL"])
def test_install_ryujinx(url: str):
    USER_CONFIGS["ryujinxInstallURL"] = os.environ.get(url, url)
    try:
        install_ryujinx()
    except Exception:
        assert url != "RYUKIT_INSTALL_URL", "Install failed for valid URL."
        return
    assert url == "RYUKIT_INSTALL_URL", "Install passed for invalid URL."


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
    with utils.capture_out() as register:
        db.CLIENT_CONFIGS.update({"echo": False})
        ls(wildcards, filters)
    db.CLIENT_CONFIGS.update({"echo": True})
    assert register.pop() == expected, "Incorrect format in output."

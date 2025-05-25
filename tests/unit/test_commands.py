import os
from typing import Literal, cast

import sqlalchemy
from pytest import mark

from ryukit.app.__context__ import USER_CONFIGS
from ryukit.app.install_ryujinx import install_ryujinx
from ryukit.app.save.apply import apply
from ryukit.app.save.create import create
from ryukit.app.save.drop import drop
from ryukit.app.save.ls import ls
from ryukit.app.save.relabel import relabel
from ryukit.libs import db

from .. import utils

__all__ = [
    "test_install_ryujinx",
    "test_save_create",
    "test_save_drop",
    "test_save_ls",
    "test_save_apply",
]


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


@mark.parametrize("url", ["BAD_URL", "RYUKIT_INSTALL_URL"])
def test_install_ryujinx(url: Literal["BAD_URL", "RYUKIT_INSTALL_URL"]):
    USER_CONFIGS["ryujinxInstallURL"] = os.environ.get(url, url)
    try:
        install_ryujinx()
    except BaseException:
        assert url == "BAD_URL", "Install failed for valid URL."
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
            "                                                                                \n  ID   LABEL            CREATED          UPDATED           LAST USED    SIZE    \n ────────────────────────────────────────────────────────────────────────────── \n  1    save202505241…   2025-05-24       2025-05-24        Never       225.7MB  \n                        13:12:36         13:12:36                               \n  2    save202505241…   2025-05-24       2025-05-24        Never       150.5MB  \n                        13:12:39         13:12:39                               \n  3    LABELLED         2025-05-24       2025-05-24        Never        0.0MB   \n                        13:13:00         13:13:00                               \n  4    save202505241…   2025-05-24       2025-05-24        Never        0.0MB   \n                        13:13:07         13:13:07                               \n  5    RELABELLED       2025-05-24       2025-05-24        Never       75.2MB   \n                        13:13:14         13:13:41.966280                        \n                                                                                \n",
        )
    ],
)
def test_save_ls(
    seed: object, wildcards: bool, filters: list[str] | None, expected: str
):
    with utils.capture_out() as register:
        ls(wildcards, filters)
    assert register.pop() == expected, "Incorrect format in output."

import datetime
import importlib
import importlib.resources
from typing import Any, cast

from pytest import mark

from ryukit import utils
from ryukit.libs import db


@mark.parametrize(
    "byte_total, expected", [(0, 0), (1048576, 1), (2097152, 2), (524288, 0.5)]
)
def test_megabytes(byte_total: int, expected: float):
    assert (
        utils.megabytes(byte_total) == expected
    ), "Incorrect byte-megabyte conversion."


@mark.parametrize(
    "obj, sizing, expected",
    [
        (
            importlib.resources.files("tests.data.saves") / "1",
            "dir",
            236666670,
        ),
        (
            importlib.resources.files("tests.data.saves") / "2",
            "dir",
            157777780,
        ),
        (importlib.resources.files("tests.data.saves") / "5", "dir", 78888890),
        (importlib.resources.files("tests.data") / "EMPTY", "dir", 0),
    ],
)
def test_size(obj: object, sizing: str, expected: int):
    assert (
        utils.size(obj, sizing=cast(Any, sizing)) == expected
    ), "Incorrect size calculation."


@mark.parametrize(
    "save_args",
    [
        {
            "id": 1,
            "label": "save20250524131236",
            "created": datetime.datetime(2025, 5, 24, 13, 12, 36),
            "updated": datetime.datetime(2025, 5, 24, 13, 12, 36),
            "last_used": None,
            "size": 0,
        },
        {
            "id": 1648,
            "label": "...",
            "created": datetime.datetime(2078, 5, 24, 13, 12, 36),
            "updated": datetime.datetime(2025, 5, 24, 13, 12, 36),
            "last_used": None,
            "size": 67880,
        },
    ],
)
def test_model_to_dict(save_args: dict[str, Any]):
    assert (
        utils.model_to_dict(db.RyujinxSave(**save_args)) == save_args
    ), "Incorrect model-dict mapping."

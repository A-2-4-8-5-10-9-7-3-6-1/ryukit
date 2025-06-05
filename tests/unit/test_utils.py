import datetime
import importlib
import importlib.resources
import pathlib
import shutil
import tempfile
from typing import Any, cast

from pytest import mark

from ryukit.libs import db
from ryukit.utils import misc

__all__ = [
    "test_megabytes",
    "test_size",
    "test_model_to_dict",
    "test_json_dumps",
]


@mark.parametrize(
    "byte_total, expected", [(0, 0), (1048576, 1), (2097152, 2), (524288, 0.5)]
)
def test_megabytes(byte_total: int, expected: float):
    assert (
        misc.megabytes(byte_total) == expected
    ), "Incorrect byte-megabyte conversion."


@mark.parametrize(
    "obj, sizing, expected",
    [
        ([1, [2], [1, [5]]], "dir", 62000010),
        ([9], "dir", 62000010),
        ([], "dir", 0),
    ],
)
def test_size(obj: object, sizing: str, expected: int) -> None:
    if sizing == "dir" and isinstance(obj, list):
        with tempfile.TemporaryDirectory() as dir:
            instructions = [(cast(list[Any], obj), dir)]
            i = -1
            while instructions:
                items, path = instructions.pop()
                while items:
                    item = items.pop()
                    i += 1
                    if isinstance(item, int):
                        for _ in range(item):
                            shutil.copy(
                                str(
                                    importlib.resources.files("tests") / "data"
                                ),
                                f"{path}/{i}",
                            )
                            i += 1
                        continue
                    pathlib.Path(f"{path}/{i}").mkdir()
                    instructions.append((item, f"{path}/{i}"))
            return test_size(dir, "dir", expected)
    assert (
        misc.size(obj, sizing=cast(Any, sizing)) == expected
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
        misc.model_to_dict(db.RyujinxSave(**save_args)) == save_args
    ), "Incorrect model-dict mapping."


@mark.parametrize(
    "data, expected",
    [
        (
            {"date": datetime.datetime(1, 1, 1, 1)},
            '{"date": "0001-01-01T01:00:00"}',
        ),
        ([1, 2, {"KEY": "VALUE"}], '[1, 2, {"KEY": "VALUE"}]'),
        ({"set": {1, 2}}, None),
    ],
)
def test_json_dumps(data: object, expected: str | None):
    try:
        assert misc.json_dumps(data) == expected, "Unexpected output."
    except ValueError:
        assert expected is None, "Error raised for valid input."

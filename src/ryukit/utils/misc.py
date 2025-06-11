"""System-wide utilities."""

import datetime
import functools
import json
import pathlib
from typing import Any, Literal

import sqlalchemy
import sqlalchemy.orm

from . import qol

__all__ = ["megabytes", "model_to_dict", "size", "json_dumps"]


def megabytes(byte_total: int, /):
    """
    Converts bytes to megabytes.

    :param byte_total: Quantity of bytes to convert.
    """

    return byte_total / pow(2, 20)


def model_to_dict(model: sqlalchemy.orm.DeclarativeBase, /) -> dict[str, Any]:
    """
    Convert a model to a dict.

    :param model: The model to convert.
    """

    return {
        column.name: getattr(model, column.name)
        for column in model.__table__.columns
    }


def size(obj: Any, /, *, sizing: Literal["dir"]):
    """
    Get the size of an object.

    :param obj: The object to be sized.
    :param sizing: The type of sizing to be done.
    """

    match sizing:
        case "dir":
            return sum(
                path.stat().st_size
                for path in pathlib.Path(obj).glob("**")
                if not path.is_dir()
            )


@qol.use
def json_dumps():
    def serialize(obj: object):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise ValueError

    return functools.partial(json.dumps, default=serialize)

"""System-wide utilities."""

import contextlib
import datetime
import functools
import io
import json
import pathlib
import sys
from collections.abc import Callable
from typing import Any, Literal

import sqlalchemy
import sqlalchemy.orm

__all__ = [
    "megabytes",
    "model_to_dict",
    "size",
    "json_dumps",
    "capture_out",
    "use",
    "PATTERNS",
]

PATTERNS: dict[
    Literal["flag_callback", "run_one", "dict_decorator"], Callable[..., Any]
] = {}


@contextlib.contextmanager
def capture_out():
    """Capture sys.stdout output within context."""

    register: list[str] = []
    with io.StringIO() as buffer:
        sys.stdout = buffer
        yield register
        sys.stdout = sys.__stdout__
        register.append(buffer.getvalue())


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


def use[R](func: Callable[..., R]):
    """Immediately use a function."""

    return func()


@use
def _():
    def dict_decorator[K, V: Callable[..., Any]](
        dict_: dict[K, V], /, *, key: K
    ):
        def inner(func: V):
            dict_[key] = func
            return func

        return inner

    dict_decorator(PATTERNS, key="dict_decorator")(dict_decorator)


@PATTERNS["dict_decorator"](PATTERNS, key="flag_callback")
def _(func: Callable[[], None], /):
    def inner(do: bool = True):
        func() if do else None

    return inner


@PATTERNS["dict_decorator"](PATTERNS, key="run_one")
@use
def _():
    used = {"$gateway": False}

    def inner(key: str, /):
        used.setdefault(key, False)

        def innner[**P](func: Callable[P, None], /):
            @functools.wraps(func)
            def core(*args: P.args, **kwargs: P.kwargs):
                if used[key]:
                    return
                func(*args, **kwargs)
                used[key] = key == "$gateway" or used["$gateway"]

            return core

        return innner

    return inner


@use
def json_dumps():
    def serialize(obj: object):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise ValueError

    return functools.partial(json.dumps, default=serialize)

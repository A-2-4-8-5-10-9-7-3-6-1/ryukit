"""Database-managent module."""

import collections
import collections.abc
import functools
import sqlite3
from typing import Callable

from ..fs import File
from . import models

__all__ = ["models", "connect"]


def tuned[**P, R](func: Callable[P, R]):
    """
    Appends a tuning stage to the end of a function.

    :param func: The function to extend.
    :returns: The extended function.
    """

    def do(tune: collections.abc.Callable[[R], object]) -> Callable[P, R]:
        @functools.wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs):
            arg = func(*args, **kwargs)
            tune(arg)
            return arg

        return inner

    if func == sqlite3.connect:
        return do(lambda conn: setattr(conn, "row_factory", sqlite3.Row))

    return func


connect = functools.partial(
    tuned(sqlite3.connect), autocommit=True, database=File.DATABASE_FILE()
)

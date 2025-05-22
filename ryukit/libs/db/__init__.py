"""Database-managent module."""

import functools
import sqlite3

from .. import paths
from . import models

__all__ = ["models", "connect"]
pconnect = functools.partial(
    sqlite3.connect, autocommit=True, database=paths.DATABASE_FILE
)


@functools.wraps(pconnect)
def connect(*args: ..., **kwargs: ...):
    conn = pconnect(*args, **kwargs)
    conn.row_factory = sqlite3.Row
    return conn

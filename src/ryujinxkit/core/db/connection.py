"""'Database connection'-related functions.

Exports
-------
- :func:`connect`: Context manager for database connection.
"""

import collections
import collections.abc
import contextlib
import sqlite3
import typing

from ..fs.resolver import Node, resolver


class ConnectionParams(typing.TypedDict, total=False):
    timeout: float
    detect_types: int
    isolation_level: (
        typing.Literal["DEFERRED", "EXCLUSIVE", "IMMEDIATE"] | None
    )
    check_same_thread: bool
    cached_statements: int
    uri: bool
    autocommit: bool


@contextlib.contextmanager
def connect(
    **connect_params: typing.Unpack[ConnectionParams],
) -> collections.abc.Generator[sqlite3.Connection]:
    """
    Get a database cursor.

    :param connect_params: Parameters for sqlite3-connect function.

    :returns: The cursor.
    """

    with sqlite3.connect(
        database=resolver[Node.RYUJINXKIT_DATABASE], **connect_params
    ) as connection:
        connection.row_factory = sqlite3.Row

        yield connection

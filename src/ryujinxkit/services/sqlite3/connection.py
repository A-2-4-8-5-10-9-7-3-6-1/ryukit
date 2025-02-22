import collections.abc
import contextlib
import sqlite3
import typing

from ...libs.fs.node import Node
from ...libs.fs.resolver import resolver


@contextlib.contextmanager
def connect(
    timeout: float = 5,
    detect_types: int = 0,
    isolation_level: (
        typing.Literal["DEFERRED", "EXCLUSIVE", "IMMEDIATE"] | None
    ) = "DEFERRED",
    check_same_thread: bool = True,
    cached_statements: int = 128,
    uri: bool = False,
    autocommit: bool = True,
) -> collections.abc.Generator[sqlite3.Connection]:
    """
    Get database cursor.

    **Notes**:
        - Parameters are those of a sqlite3.connect object.

    :returns: The cursor.
    """

    with sqlite3.connect(
        database=resolver[Node.RYUJINXKIT_DATABASE],
        timeout=timeout,
        detect_types=detect_types,
        isolation_level=isolation_level,
        check_same_thread=check_same_thread,
        cached_statements=cached_statements,
        uri=uri,
        autocommit=autocommit,
    ) as connection:
        yield connection

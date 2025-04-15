"""Database-managent module."""

import collections
import collections.abc
import sqlite3
import typing

from ...libs import theming
from .. import fs
from . import models

__all__ = ["models", "theme"]


# MARK: Theming


def annotate_theme[**P, R](applier: collections.abc.Callable[P, R]):
    def annotated_applier(*args: P.args, **kwargs: P.kwargs) -> R:
        """
        Sets defaults for database-oriented functions.

        Theme Guide
        -----------

        - sqlite3.connect(defaults=[autocommit]): Database paths are automatically handled. Set the 'database' parameter, via keyword argument, to a string like 'DATABASE'.
        """

        return applier(*args, **kwargs)

    return annotated_applier


def sql_connect_preprocessor(
    database: object, *rest: object, **kwargs: object
):
    return ((fs.File.DATABASE_FILE(), *rest), kwargs)


theme = annotate_theme(
    theming.theme_applier(
        {
            sqlite3.connect: {
                "default_kwargs": {"autocommit": True},
                "preprocessor": sql_connect_preprocessor,
                "postprocessor": lambda conn: typing.cast(
                    sqlite3.Connection, conn
                ).__setattr__("row_factory", sqlite3.Row)
                or conn,
            }
        }
    )
)

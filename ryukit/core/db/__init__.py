"""Database-managent module."""

import collections
import collections.abc
import sqlite3

from ...libs import theming
from .. import fs
from . import models

__all__ = ["models", "theme_applier"]


# MARK: Theming


def annotate_theme[**P, R](applier: collections.abc.Callable[P, R]):
    def annotated_applier(*args: P.args, **kwargs: P.kwargs) -> R:
        """
        Hook for setting parameter defaults for database functions.

        Theme Guide
        ===========

        sqlite3.connect
        ---------------

        Default kwargs:

        - autocommit
        - detect_types

        The database path is handled by the preprocessor, set it, as a positional parameter, to a placeholder ("DATABASE" is recommended).
        """

        return applier(*args, **kwargs)

    return annotated_applier


def sql_connect_PPR(database: object, *rest: object, **kwargs: object):
    return ((fs.File.DATABASE_FILE(), *rest), kwargs)


theme_applier = annotate_theme(
    theming.theme_applier(
        {
            sqlite3.connect: {
                "default_kwargs": {"autocommit": True, "detect_types": 1},
                "preprocessor": sql_connect_PPR,
            }
        }
    )
)

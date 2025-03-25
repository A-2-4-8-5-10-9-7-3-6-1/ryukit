"""Database theme-applier definitions."""

import sqlite3

import theming
import theming.functional_theming

from ..fs.resolver import Node, resolver


def _connect_PPR(database: object, *rest: object, **kwargs: object):
    return rest, kwargs


db_ready = theming.functional_theming.theme_applier(
    {
        sqlite3.connect: {
            "default_kwargs": {"database": resolver[Node.RYUJINXKIT_DATABASE]},
            "preprocessor": _connect_PPR,
        }
    }
)

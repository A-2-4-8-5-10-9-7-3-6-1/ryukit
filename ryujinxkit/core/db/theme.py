"""
Theme Guide
===========

sqlite3.connect
---------------

Default kwargs;

- autocommit
- detect_types

The database argument should be passed positionally; it's discarded by the \
preprocessor, so it can be set to any placeholder --- though "DATABASE" is \
recommended for consistency.
"""

import sqlite3

import theming
import theming.functional_theming

from ..fs.resolver import Node, resolver


def _connect_PPR(database: object, *rest: object, **kwargs: object):
    return (resolver[Node.RYUJINXKIT_DATABASE], *rest), kwargs


db_applier = theming.functional_theming.theme_applier(
    {
        sqlite3.connect: {
            "default_kwargs": {"autocommit": True, "detect_types": 1},
            "preprocessor": _connect_PPR,
        }
    }
)

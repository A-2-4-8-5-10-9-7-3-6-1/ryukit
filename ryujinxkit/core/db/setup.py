"""Database setup script."""

import importlib
import importlib.resources
import sqlite3

from .theme import db_applier

with db_applier(sqlite3.connect)("DATABASE") as con:
    con.executescript(
        (
            importlib.resources.files("ryujinxkit")
            / "assets"
            / "database-setup.sql"
        ).read_text()
    )

__all__ = []

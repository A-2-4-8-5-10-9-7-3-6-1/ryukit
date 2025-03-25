"""Database setup script."""

import importlib
import importlib.resources
import sqlite3

from .theme_applier import db_ready

with db_ready(sqlite3.connect)("DATABASE") as _con:
    _con.execute(
        (
            importlib.resources.files("ryujinxkit")
            / "assests"
            / "database-setup.sql"
        ).read_text()
    )

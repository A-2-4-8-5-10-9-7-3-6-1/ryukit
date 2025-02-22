from .libs.fs.node import Node
from .libs.fs.resolver import resolver
from .services.sqlite3.connection import connect

[
    resolver[node].mkdir(parents=True, exist_ok=True)
    for node in [
        Node.RYUJINXKIT_ROAMING_DATA,
        Node.RYUJINX_ROAMING_DATA,
        Node.RYUJINXKIT_SAVE_FOLDER,
    ]
]

with connect() as connection:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS saves (
            id INTEGER,
            tag VARCHAR(20) DEFAULT untagged,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used TIMESTAMP,
            size INTEGER DEFAULT 0,
            PRIMARY KEY (id)
        );
        """
    )

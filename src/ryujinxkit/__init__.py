from .database.connection import connect
from .file_access.resolver import resolver
from .file_access.resolver_node import ResolverNode

__all__ = []


[
    resolver[node].mkdir(parents=True, exist_ok=True)
    for node in [
        ResolverNode.RYUJINXKIT_ROAMING_DATA,
        ResolverNode.RYUJINX_ROAMING_DATA,
        ResolverNode.RYUJINXKIT_SAVE_FOLDER,
        ResolverNode.RYUJINXKIT_CONFIGS,
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

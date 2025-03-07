from .connection import connect

with connect() as connection:
    connection.execute(
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

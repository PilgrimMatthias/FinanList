import sqlite3
from pathlib import Path
from contextlib import contextmanager


class Database:
    """Handles database connection and invoking sql queries."""

    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.connection = sqlite3.connect(self.path)

        # Turns on foreign keys and ON DELETE CASCADE
        self.connection.execute("PRAGMA foreign_keys = ON")

        self._init_schema(self)

    def _init_schema(self):
        """
        Create database schema using script schema.sql
        """
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path) as file:
            self.connection.executescript(file.read())

    @contextmanager
    def transaction(self):
        try:
            yield
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def execute(self, query: str, params: tuple = ()):
        return self.connection.execute(query, params)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

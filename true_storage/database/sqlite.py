"""SQLite-based storage implementation."""

import pickle
import sqlite3
import threading
from typing import Optional, Any

from ..base import BaseStorage
from ..exceptions import StorageError


class SQLiteStorage(BaseStorage):
    """SQLite-based storage implementation."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or ":memory:"
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS checkpoints (
                        key TEXT PRIMARY KEY,
                        value BLOB
                    )
                """)
                conn.commit()
                conn.close()
            except Exception as e:
                raise StorageError(f"Failed to initialize database: {e}")

    def store(self, key: str, value: Any) -> None:
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                value_bytes = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                conn.execute(
                    "INSERT OR REPLACE INTO checkpoints (key, value) VALUES (?, ?)",
                    (key, value_bytes)
                )
                conn.commit()
                conn.close()
            except Exception as e:
                raise StorageError(f"Failed to store value: {e}")

    def retrieve(self, key: str) -> Any:
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute(
                    "SELECT value FROM checkpoints WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                conn.close()

                if row is None:
                    raise KeyError(f"No value found for key: {key}")
                return pickle.loads(row[0])
            except KeyError:
                raise
            except Exception as e:
                raise StorageError(f"Failed to retrieve value: {e}")

    def delete(self, key: str) -> None:
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("DELETE FROM checkpoints WHERE key = ?", (key,))
                conn.commit()
                conn.close()
            except Exception as e:
                raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("DELETE FROM checkpoints")
                conn.commit()
                conn.close()
            except Exception as e:
                raise StorageError(f"Failed to clear storage: {e}")

    def clone(self) -> 'SQLiteStorage':
        new_storage = SQLiteStorage(":memory:")
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute("SELECT key, value FROM checkpoints")
                for key, value_bytes in cursor:
                    value = pickle.loads(value_bytes)
                    new_storage.store(key, value)
                conn.close()
                return new_storage
            except Exception as e:
                new_storage.clear()
                raise StorageError(f"Failed to clone storage: {e}")

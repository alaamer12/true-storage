"""SQLite-based database storage module.

This module provides a persistent storage implementation using SQLite,
offering ACID-compliant transactions and efficient data storage.

Classes:
    SQLiteStorage: Main class implementing SQLite-based storage functionality.

Functions:
    None (all functionality is encapsulated in classes)

Types:
    None

Exceptions:
    StorageError: See :exc:`true_storage.exceptions.StorageError`
    KeyError: Raised when accessing non-existent keys

Key Features:
    - ACID-compliant transactions
    - Thread-safe operations
    - In-memory or file-based storage
    - Binary data support
    - Automatic connection management
    - Connection pooling
    - Resource cleanup
    - SQL-based querying capabilities
"""

import pickle
import sqlite3
import threading
from typing import Any, Optional, List

from ..exceptions import StorageError
from true_storage.base import BaseStorage

__all__ = [
    'SQLiteStorage',
]

def __dir__() -> List[str]:
    return sorted(__all__)

"""SQLite-based storage implementation."""

class SQLiteStorage(BaseStorage):
    """SQLite-based storage implementation."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize SQLite storage.
        
        Args:
            db_path: Path to SQLite database file. If None, uses in-memory database.
        """
        self.db_path = db_path or ":memory:"
        self._lock = threading.RLock()
        self._conn = None
        self._init_db()

    def _get_connection(self):
        """Get a SQLite connection, creating it if needed."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._conn

    def _init_db(self):
        """Initialize the database schema."""
        with self._lock:
            try:
                conn = self._get_connection()
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS checkpoints (
                        key TEXT PRIMARY KEY,
                        value BLOB
                    )
                """)
                conn.commit()
            except Exception as e:
                raise StorageError(f"Failed to initialize database: {e}")

    def store(self, key: str, value: Any) -> None:
        """Store a value in the database."""
        with self._lock:
            try:
                conn = self._get_connection()
                value_bytes = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                conn.execute(
                    "INSERT OR REPLACE INTO checkpoints (key, value) VALUES (?, ?)",
                    (key, value_bytes)
                )
                conn.commit()
            except Exception as e:
                raise StorageError(f"Failed to store value: {e}")

    def retrieve(self, key: str) -> Any:
        """Retrieve a value from the database."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.execute(
                    "SELECT value FROM checkpoints WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()

                if row is None:
                    raise KeyError(f"No value found for key: {key}")
                return pickle.loads(row[0])
            except KeyError:
                raise
            except Exception as e:
                raise StorageError(f"Failed to retrieve value: {e}")

    def delete(self, key: str) -> None:
        """Delete a value from the database."""
        with self._lock:
            try:
                conn = self._get_connection()
                conn.execute("DELETE FROM checkpoints WHERE key = ?", (key,))
                conn.commit()
            except Exception as e:
                raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        """Clear all values from the database."""
        with self._lock:
            try:
                conn = self._get_connection()
                conn.execute("DELETE FROM checkpoints")
                conn.commit()
            except Exception as e:
                raise StorageError(f"Failed to clear storage: {e}")

    def close(self):
        """Close the database connection."""
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def clone(self) -> 'BaseStorage':
        ...

    def __del__(self):
        """Ensure connection is closed on deletion."""
        self.close()

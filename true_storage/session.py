"""Session store implementation with expiration and cleanup."""

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, Iterator

from true_storage.exceptions import StorageError


@dataclass
class SessionStoreConfig:
    """Configuration for SessionStore."""
    max_size: int = 1000
    expiration_time: int = 3600  # 1 hour
    cleanup_interval: int = 60  # 1 minute


class SessionStore:
    """A robust and thread-safe in-memory session store with expiration and LRU eviction."""

    def __init__(self, config: SessionStoreConfig = None):
        self.config = config or SessionStoreConfig()
        self._store: OrderedDict = OrderedDict()
        self._timestamps: Dict[Any, float] = {}
        self._lock = threading.Lock()
        self._stop_cleanup = threading.Event()
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_expired_sessions,
            daemon=True
        )
        self._cleanup_thread.start()

    def set(self, key: Any, value: Any) -> None:
        """Set a session key to a value with the current timestamp."""
        with self._lock:
            try:
                if len(self._store) >= self.config.max_size:
                    # Remove oldest item if at capacity
                    self._store.popitem(last=False)
                timestamp = time.time()
                self._store[key] = value
                self._timestamps[key] = timestamp
                print(f"Set key: {key} with expiration at {timestamp + self.config.expiration_time}")
            except Exception as e:
                raise StorageError(f"Failed to set value: {e}")

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        """Retrieve a session value by key. Returns default if key is not found or expired."""
        with self._lock:
            try:
                if key not in self._store:
                    return default
                
                timestamp = self._timestamps[key]
                if time.time() - timestamp > self.config.expiration_time:
                    self.delete(key)
                    return default
                
                print(f"Accessed key: {key}")
                return self._store[key]
            except Exception as e:
                raise StorageError(f"Failed to get value: {e}")

    def delete(self, key: Any) -> bool:
        """Delete a session key. Returns True if the key was deleted, False if not found."""
        with self._lock:
            try:
                if key in self._store:
                    del self._store[key]
                    del self._timestamps[key]
                    return True
                return False
            except Exception as e:
                raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        """Clear all sessions."""
        with self._lock:
            try:
                self._store.clear()
                self._timestamps.clear()
            except Exception as e:
                raise StorageError(f"Failed to clear sessions: {e}")

    def keys(self) -> Iterator[Any]:
        """Return an iterator over the session keys."""
        with self._lock:
            return iter(self._store.keys())

    def values(self) -> Iterator[Any]:
        """Return an iterator over the session values."""
        with self._lock:
            return iter(self._store.values())

    def items(self) -> Iterator[tuple[Any, Any]]:
        """Return an iterator over the session items (key, value)."""
        with self._lock:
            return iter(self._store.items())

    def _cleanup_expired_sessions(self) -> None:
        """Background thread method to clean up expired sessions periodically."""
        while not self._stop_cleanup.is_set():
            with self._lock:
                current_time = time.time()
                expired_keys = [
                    key for key, timestamp in self._timestamps.items()
                    if current_time - timestamp > self.config.expiration_time
                ]
                for key in expired_keys:
                    self.delete(key)
            self._stop_cleanup.wait(self.config.cleanup_interval)

    def stop_cleanup(self) -> None:
        """Stop the background cleanup thread."""
        self._stop_cleanup.set()
        self._cleanup_thread.join()
        print("Cleanup thread stopped.")

    def __del__(self):
        """Ensure the cleanup thread is stopped when the instance is deleted."""
        self.stop_cleanup()

    def __setitem__(self, key: Any, value: Any) -> None:
        """Enable dict-like setting of items."""
        self.set(key, value)

    def __getitem__(self, key: Any) -> Any:
        """Enable dict-like getting of items."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __delitem__(self, key: Any) -> None:
        """Enable dict-like deletion of items."""
        if not self.delete(key):
            raise KeyError(key)

    def __contains__(self, key: Any) -> bool:
        """Enable use of 'in' keyword to check for key existence."""
        return self.get(key) is not None

    def __len__(self) -> int:
        """Return the number of active (non-expired) sessions."""
        with self._lock:
            current_time = time.time()
            return sum(
                1 for timestamp in self._timestamps.values()
                if current_time - timestamp <= self.config.expiration_time
            )

    def __repr__(self) -> str:
        return f"SessionStore(size={len(self)}, max_size={self.config.max_size})"

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SessionStore):
            return NotImplemented
        return (
            self.config.max_size == other.config.max_size and
            self.config.expiration_time == other.config.expiration_time and
            self._store == other._store
        )

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, SessionStore):
            return NotImplemented
        return len(self) <= len(other)

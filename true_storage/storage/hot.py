"""Hot storage implementation with LRU cache."""

import threading
import time
from collections import OrderedDict
from typing import Any

from ..base import BaseStorage
from ..exceptions import StorageError


class HotStorage(BaseStorage):
    """Hot storage implementation with LRU cache."""

    def __init__(self, max_size=100, expiration_time=300):
        self.data = OrderedDict()  # Maintains insertion order
        self.max_size = max_size
        self.expiration_time = expiration_time  # Time in seconds
        self.lock = threading.Lock()  # For thread-safe access
        self._timestamps = {}  # Store timestamps for each key

    def _remove_expired_items(self):
        """Remove expired items from storage."""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._timestamps.items()
            if current_time - timestamp > self.expiration_time
        ]
        for key in expired_keys:
            self.delete(key)

    def store(self, key: str, value: Any) -> None:
        with self.lock:
            try:
                self._remove_expired_items()
                if key in self.data:
                    del self.data[key]
                elif len(self.data) >= self.max_size:
                    self.data.popitem(last=False)  # Remove oldest item
                self.data[key] = value
                self._timestamps[key] = time.time()
            except Exception as e:
                raise StorageError(f"Failed to store value: {e}")

    def retrieve(self, key: str) -> Any:
        with self.lock:
            try:
                self._remove_expired_items()
                if key not in self.data:
                    return None
                value = self.data.pop(key)  # Remove and re-add to maintain LRU order
                self.data[key] = value
                self._timestamps[key] = time.time()  # Update timestamp
                return value
            except Exception as e:
                raise StorageError(f"Failed to retrieve value: {e}")

    def delete(self, key: str) -> None:
        with self.lock:
            try:
                if key in self.data:
                    del self.data[key]
                    del self._timestamps[key]
            except Exception as e:
                raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        with self.lock:
            try:
                self.data.clear()
                self._timestamps.clear()
            except Exception as e:
                raise StorageError(f"Failed to clear storage: {e}")

    def clone(self) -> 'HotStorage':
        new_storage = HotStorage(self.max_size, self.expiration_time)
        with self.lock:
            try:
                new_storage.data = OrderedDict(self.data)
                new_storage._timestamps = dict(self._timestamps)
                return new_storage
            except Exception as e:
                new_storage.clear()
                raise StorageError(f"Failed to clone storage: {e}")

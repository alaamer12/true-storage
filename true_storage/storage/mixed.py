"""Mixed storage implementation combining hot and cold storage."""

import threading
from typing import Any

from .hot import HotStorage
from .cold import ColdStorage
from ..exceptions import StorageError


class MixedStorage:
    """Mixed storage implementation combining hot and cold storage."""

    def __init__(self, max_size=100, expiration_time=300):
        self.hot_storage = HotStorage(max_size, expiration_time)
        self.cold_storage = ColdStorage()
        self._lock = threading.Lock()

    def store_session(self, session_id: str, session_data: Any) -> None:
        """Store session data in both hot and cold storage."""
        with self._lock:
            try:
                self.hot_storage.store(session_id, session_data)
                self.cold_storage.store(session_id, session_data)
            except Exception as e:
                raise StorageError(f"Failed to store session: {e}")

    def retrieve_session(self, session_id: str) -> Any:
        """Retrieve session data from hot storage first, then cold storage."""
        with self._lock:
            try:
                # Try hot storage first
                data = self.hot_storage.retrieve(session_id)
                if data is not None:
                    return data

                # If not in hot storage, try cold storage
                data = self.cold_storage.retrieve(session_id)
                if data is not None:
                    # Store in hot storage for future quick access
                    self.hot_storage.store(session_id, data)
                return data
            except KeyError:
                return None
            except Exception as e:
                raise StorageError(f"Failed to retrieve session: {e}")

    def delete_session(self, session_id: str) -> None:
        """Delete session data from both hot and cold storage."""
        with self._lock:
            try:
                self.hot_storage.delete(session_id)
                self.cold_storage.delete(session_id)
            except Exception as e:
                raise StorageError(f"Failed to delete session: {e}")

    def clear_storage(self) -> None:
        """Clear both hot and cold storage."""
        with self._lock:
            try:
                self.hot_storage.clear()
                self.cold_storage.clear()
            except Exception as e:
                raise StorageError(f"Failed to clear storage: {e}")

    def __del__(self):
        """Clean up resources when the object is deleted."""
        self.clear_storage()

    def __repr__(self):
        return f"MixedStorage(max_size={self.hot_storage.max_size}, expiration_time={self.hot_storage.expiration_time})"

    def __str__(self):
        return self.__repr__()

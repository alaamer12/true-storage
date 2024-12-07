"""Mixed storage module combining hot and cold storage capabilities.

This module implements a hybrid storage system that leverages both in-memory (hot) and
disk-based (cold) storage for optimal performance and data persistence.

Classes:
    MixedStorage: Main class implementing hybrid storage functionality.
    StoragePolicy: Enumeration of possible storage policies. (imported from base.py)

Functions:
    None (all functionality is encapsulated in classes)

Types:
    None

Exceptions:
    StorageError: Raised when storage operations fail

Key Features:
    - Hybrid storage combining hot and cold storage benefits
    - Automatic data synchronization between storage layers
    - Intelligent data retrieval strategy
    - Performance metrics for both storage layers
    - Storage optimization capabilities
    - Hot storage warm-up functionality
    - Thread-safe operations
    - Event emission system
    - Configurable storage policies
"""

import threading
import time
from typing import Any, Optional, Dict, List

from .base import (
    BaseStorageManager,
    StoragePolicy,
    StorageStrategy
)
from .cold import ColdStorage
from .hot import HotStorage
from ..exceptions import StorageError


__all__ = [
    'MixedStorage',
    'StoragePolicy',
    'StorageError'
]

def __dir__() -> List[str]:
    return sorted(__all__)


class MixedStorageStrategy(StorageStrategy):
    """Strategy for mixed storage operations."""

    def __init__(self, hot_storage: HotStorage, cold_storage: ColdStorage):
        self.hot_storage = hot_storage
        self.cold_storage = cold_storage
        self.lock = threading.Lock()

    def store(self, key: str, value: Any) -> None:
        """Store value in both hot and cold storage."""
        with self.lock:
            self.hot_storage.store(key, value)
            self.cold_storage.store(key, value)

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from hot storage first, then cold storage."""
        with self.lock:
            # Try hot storage first
            value = self.hot_storage.retrieve(key)
            if value is not None:
                return value

            # If not in hot storage, try cold storage
            value = self.cold_storage.retrieve(key)
            if value is not None:
                # Store in hot storage for future quick access
                self.hot_storage.store(key, value)
            return value

    def delete(self, key: str) -> None:
        """Delete value from both hot and cold storage."""
        with self.lock:
            self.hot_storage.delete(key)
            self.cold_storage.delete(key)


class MixedStorage(BaseStorageManager):
    """Mixed storage implementation combining hot and cold storage."""

    def __init__(
            self,
            storage_id: str = "mixed_storage",
            max_size: int = 100,
            expiration_time: int = 300,
            storage_directory: str = "cold_storage",
            compression_level: int = 6,
            policy: StoragePolicy = StoragePolicy.STRICT
    ):
        super().__init__(
            storage_id=storage_id,
            policy=policy
        )
        self.hot_storage = HotStorage(
            storage_id=f"{storage_id}_hot",
            max_size=max_size,
            expiration_time=expiration_time,
            policy=policy
        )
        self.cold_storage = ColdStorage(
            storage_id=f"{storage_id}_cold",
            storage_directory=storage_directory,
            compression_level=compression_level,
            policy=policy
        )
        self.strategy = MixedStorageStrategy(self.hot_storage, self.cold_storage)

    def store(self, key: str, value: Any) -> None:
        """Store a value in mixed storage."""
        start_time = time.time()
        success = True
        try:
            self.strategy.store(key, value)
            self.emit_event("item_stored", {"key": key})
            self._trigger_callbacks("after_store", key, value)
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to store value: {e}")
        finally:
            self.update_metrics("store", success, time.time() - start_time)

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from mixed storage."""
        start_time = time.time()
        success = True
        try:
            value = self.strategy.retrieve(key)
            if value is not None:
                self.emit_event("item_retrieved", {"key": key})
                self._trigger_callbacks("after_retrieve", key, value)
            return value
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to retrieve value: {e}")
            return None
        finally:
            self.update_metrics("retrieve", success, time.time() - start_time)

    def delete(self, key: str) -> None:
        """Delete a value from mixed storage."""
        start_time = time.time()
        success = True
        try:
            self.strategy.delete(key)
            self.emit_event("item_deleted", {"key": key})
            self._trigger_callbacks("after_delete", key)
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to delete value: {e}")
        finally:
            self.update_metrics("delete", success, time.time() - start_time)

    def clear(self) -> None:
        """Clear all items from mixed storage."""
        start_time = time.time()
        success = True
        try:
            self.hot_storage.clear()
            self.cold_storage.clear()
            self.emit_event("storage_cleared")
            self._trigger_callbacks("after_clear")
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to clear storage: {e}")
        finally:
            self.update_metrics("clear", success, time.time() - start_time)

    def get_hot_stats(self) -> Dict[str, Any]:
        """Get hot storage statistics."""
        return self.hot_storage.get_stats()

    def get_cold_stats(self) -> Dict[str, Any]:
        """Get cold storage statistics."""
        return self.cold_storage.get_stats()

    def get_stats(self) -> Dict[str, Any]:
        """Get combined storage statistics."""
        hot_stats = self.get_hot_stats()
        cold_stats = self.get_cold_stats()
        metrics = self.get_metrics()

        return {
            "hot_storage": hot_stats,
            "cold_storage": cold_stats,
            "combined": {
                "total_operations": metrics.total_operations,
                "total_errors": metrics.total_errors,
                "avg_response_time": metrics.avg_response_time,
                "hit_ratio": metrics.hits / (metrics.hits + metrics.misses) if metrics.hits + metrics.misses > 0 else 0
            }
        }

    def get_keys(self) -> list[str]:
        """Get all keys from both hot and cold storage."""
        hot_keys = set(self.hot_storage.get_keys())
        cold_keys = set(self.cold_storage.get_keys())
        return list(hot_keys | cold_keys)

    def optimize_hot_storage(self) -> None:
        """Optimize hot storage by removing least accessed items."""
        keys = self.hot_storage.get_keys()
        if not keys:
            return

        # Move least accessed items to cold storage only
        for key in keys:
            value = self.hot_storage.retrieve(key)
            if value is not None:
                self.cold_storage.store(key, value)
                self.hot_storage.delete(key)

    def warm_up_hot_storage(self, keys: list[str]) -> None:
        """Pre-load specified keys into hot storage."""
        for key in keys:
            value = self.cold_storage.retrieve(key)
            if value is not None:
                self.hot_storage.store(key, value)

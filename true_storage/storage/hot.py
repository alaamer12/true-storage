"""Hot storage module providing fast in-memory caching with LRU eviction strategy.

This module implements a high-performance hot storage system using LRU (Least Recently Used)
caching mechanism with features like expiration, optimization, and event handling.

Classes:
    HotStorage: Main class implementing hot storage functionality.
    StoragePolicy: Enumeration of possible storage policies. (you can import it from base.py)

Functions:
    None (all functionality is encapsulated in classes)

Types:
    None

Exceptions:
    StorageError: Raised when storage operations fail

Key Features:
    - LRU (Least Recently Used) caching strategy
    - Thread-safe operations
    - Automatic item expiration
    - Data optimization support
    - Event emission system
    - Performance metrics tracking
    - Configurable storage policies
    - Callback system for storage events
"""

import threading
import time
from collections import OrderedDict
from typing import Any, Optional, Dict, List

from .base import (
    BaseStorageManager,
    StoragePolicy,
    StorageStrategy,
    StorageOptimizer
)
from ..exceptions import StorageError


__all__ = [
    'HotStorage',
    'StoragePolicy',
    'StorageError'
]

def __dir__() -> List[str]:
    return sorted(__all__)

class LRUOptimizer(StorageOptimizer):
    """Optimizer for LRU cache data."""

    def optimize(self, data: Any) -> Any:
        """Optimize data for storage."""
        # Add optimization logic here if needed
        return data

    def deoptimize(self, data: Any) -> Any:
        """Restore data from optimized form."""
        # Add deoptimization logic here if needed
        return data


class LRUStrategy(StorageStrategy):
    """LRU cache implementation strategy."""

    def __init__(self, max_size: int):
        self.data: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.lock = threading.Lock()

    def store(self, key: str, value: Any) -> None:
        """Store a value using LRU strategy."""
        with self.lock:
            if key in self.data:
                del self.data[key]
            elif len(self.data) >= self.max_size:
                self.data.popitem(last=False)
            self.data[key] = value

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value using LRU strategy."""
        with self.lock:
            if key not in self.data:
                return None
            value = self.data.pop(key)
            self.data[key] = value
            return value

    def delete(self, key: str) -> None:
        """Delete a value using LRU strategy."""
        with self.lock:
            if key in self.data:
                del self.data[key]


class HotStorage(BaseStorageManager):
    """Hot storage implementation with LRU cache and advanced features."""

    def __init__(
            self,
            storage_id: str = "hot_storage",
            max_size: int = 100,
            expiration_time: int = 300,
            policy: StoragePolicy = StoragePolicy.STRICT
    ):
        super().__init__(
            storage_id=storage_id,
            policy=policy,
            optimizer=LRUOptimizer()
        )
        self.expiration_time = expiration_time
        self.strategy = LRUStrategy(max_size)
        self._timestamps: Dict[str, float] = {}

    def _is_expired(self, key: str) -> bool:
        """Check if a key has expired."""
        timestamp = self._timestamps.get(key)
        if timestamp is None:
            return True
        return time.time() - timestamp > self.expiration_time

    def _remove_expired_items(self) -> None:
        """Remove expired items from storage."""
        expired_keys = [
            key for key in list(self._timestamps.keys())
            if self._is_expired(key)
        ]
        for key in expired_keys:
            self.delete(key)
            self.emit_event("item_expired", {"key": key})

    def store(self, key: str, value: Any) -> None:
        """Store a value in hot storage."""
        start_time = time.time()
        success = True
        try:
            self._remove_expired_items()
            optimized_value = self.optimize_data(value)
            self.strategy.store(key, optimized_value)
            self._timestamps[key] = time.time()
            self.emit_event("item_stored", {"key": key})
            self._trigger_callbacks("after_store", key, value)
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to store value: {e}")
        finally:
            self.update_metrics("store", success, time.time() - start_time)

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from hot storage."""
        start_time = time.time()
        success = True
        try:
            self._remove_expired_items()
            if self._is_expired(key):
                self.delete(key)
                return None

            value = self.strategy.retrieve(key)
            if value is not None:
                value = self.deoptimize_data(value)
                self._timestamps[key] = time.time()  # Update access time
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
        """Delete a value from hot storage."""
        start_time = time.time()
        success = True
        try:
            self.strategy.delete(key)
            self._timestamps.pop(key, None)
            self.emit_event("item_deleted", {"key": key})
            self._trigger_callbacks("after_delete", key)
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to delete value: {e}")
        finally:
            self.update_metrics("delete", success, time.time() - start_time)

    def clear(self) -> None:
        """Clear all items from hot storage."""
        start_time = time.time()
        success = True
        try:
            self.strategy = LRUStrategy(self.strategy.max_size)
            self._timestamps.clear()
            self.emit_event("storage_cleared")
            self._trigger_callbacks("after_clear")
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to clear storage: {e}")
        finally:
            self.update_metrics("clear", success, time.time() - start_time)

    def get_size(self) -> int:
        """Get the current size of hot storage."""
        return len(self._timestamps)

    def get_keys(self) -> list[str]:
        """Get all non-expired keys in hot storage."""
        self._remove_expired_items()
        return list(self._timestamps.keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        metrics = self.get_metrics()
        return {
            "size": self.get_size(),
            "max_size": self.strategy.max_size,
            "hit_ratio": metrics.hits / (metrics.hits + metrics.misses) if metrics.hits + metrics.misses > 0 else 0,
            "avg_response_time": metrics.avg_response_time,
            "total_operations": metrics.total_operations,
            "total_errors": metrics.total_errors
        }

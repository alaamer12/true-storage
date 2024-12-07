"""Cold storage module providing persistent disk-based storage with compression.

This module implements a disk-based storage system with data compression and metadata
tracking for efficient long-term data storage.

Classes:
    ColdStorage: Main class implementing cold storage functionality.
    StoragePolicy: Enumeration of possible storage policies. (imported from base.py)

Functions:
    None (all functionality is encapsulated in classes)

Types:
    None

Exceptions:
    StorageError: Raised when storage operations fail

Key Features:
    - File system based persistent storage
    - Data compression using zlib
    - Metadata tracking for stored items
    - Thread-safe operations
    - Performance metrics tracking
    - Event emission system
    - Configurable storage policies
    - Automatic directory management
    - Size and statistics tracking
"""

import json
import os
import pickle
import threading
import time
import zlib
from typing import Any, Optional, Dict, List

from .base import (
    BaseStorageManager,
    StoragePolicy,
    StorageStrategy,
    StorageOptimizer
)
from ..exceptions import StorageError


__all__ = [
    'ColdStorage',
    'StoragePolicy',
    'StorageError'
]

def __dir__() -> List[str]:
    return sorted(__all__)


class CompressionOptimizer(StorageOptimizer):
    """Optimizer for compressed data storage."""

    def __init__(self, compression_level: int = 6):
        self.compression_level = compression_level

    def optimize(self, data: Any) -> bytes:
        """Compress data using zlib."""
        try:
            pickled_data = pickle.dumps(data)
            return zlib.compress(pickled_data, self.compression_level)
        except Exception as e:
            raise StorageError(f"Failed to compress data: {e}")

    def deoptimize(self, data: bytes) -> Any:
        """Decompress data using zlib."""
        try:
            decompressed_data = zlib.decompress(data)
            return pickle.loads(decompressed_data)
        except Exception as e:
            raise StorageError(f"Failed to decompress data: {e}")


class FileSystemStrategy(StorageStrategy):
    """File system storage strategy."""

    def __init__(self, storage_directory: str):
        self.storage_directory = storage_directory
        self.lock = threading.Lock()
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """Create the storage directory if it does not exist."""
        os.makedirs(self.storage_directory, exist_ok=True)

    def _get_file_path(self, key: str) -> str:
        """Get the file path for a key."""
        return os.path.join(self.storage_directory, f"{key}.bin")

    def store(self, key: str, value: bytes) -> None:
        """Store compressed data to file."""
        with self.lock:
            try:
                file_path = self._get_file_path(key)
                with open(file_path, 'wb') as f:
                    f.write(value)
            except Exception as e:
                raise StorageError(f"Failed to store file: {e}")

    def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve compressed data from file."""
        with self.lock:
            try:
                file_path = self._get_file_path(key)
                if not os.path.exists(file_path):
                    return None
                with open(file_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                raise StorageError(f"Failed to retrieve file: {e}")

    def delete(self, key: str) -> None:
        """Delete a file."""
        with self.lock:
            try:
                file_path = self._get_file_path(key)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                raise StorageError(f"Failed to delete file: {e}")


class ColdStorage(BaseStorageManager):
    """Cold storage implementation with compression and advanced features."""

    def __init__(
            self,
            storage_id: str = "cold_storage",
            storage_directory: str = "cold_storage",
            compression_level: int = 6,
            policy: StoragePolicy = StoragePolicy.STRICT
    ):
        super().__init__(
            storage_id=storage_id,
            policy=policy,
            optimizer=CompressionOptimizer(compression_level)
        )
        self.strategy = FileSystemStrategy(storage_directory)
        self.metadata: Dict[str, Dict] = {}
        self._metadata_file = os.path.join(storage_directory, "metadata.json")
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load metadata from JSON file."""
        try:
            if os.path.exists(self._metadata_file):
                with open(self._metadata_file, 'r') as f:
                    self.metadata = json.load(f)
        except Exception as e:
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to load metadata: {e}")
            self.metadata = {}

    def _save_metadata(self) -> None:
        """Save metadata to JSON file."""
        try:
            with open(self._metadata_file, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to save metadata: {e}")

    def store(self, key: str, value: Any) -> None:
        """Store a value in cold storage."""
        start_time = time.time()
        success = True
        try:
            compressed_data = self.optimize_data(value)
            self.strategy.store(key, compressed_data)

            # Update metadata
            self.metadata[key] = {
                "size": len(compressed_data),
                "created_at": time.time(),
                "last_accessed": time.time()
            }
            self._save_metadata()

            self.emit_event("item_stored", {
                "key": key,
                "size": len(compressed_data)
            })
            self._trigger_callbacks("after_store", key, value)
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to store value: {e}")
        finally:
            self.update_metrics("store", success, time.time() - start_time)

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from cold storage."""
        start_time = time.time()
        success = True
        try:
            compressed_data = self.strategy.retrieve(key)
            if compressed_data is None:
                return None

            value = self.deoptimize_data(compressed_data)

            # Update metadata
            if key in self.metadata:
                self.metadata[key]["last_accessed"] = time.time()
                self._save_metadata()

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
        """Delete a value from cold storage."""
        start_time = time.time()
        success = True
        try:
            self.strategy.delete(key)
            self.metadata.pop(key, None)
            self._save_metadata()

            self.emit_event("item_deleted", {"key": key})
            self._trigger_callbacks("after_delete", key)
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to delete value: {e}")
        finally:
            self.update_metrics("delete", success, time.time() - start_time)

    def clear(self) -> None:
        """Clear all items from cold storage."""
        start_time = time.time()
        success = True
        try:
            for key in list(self.metadata.keys()):
                self.delete(key)
            self.metadata.clear()
            self._save_metadata()

            self.emit_event("storage_cleared")
            self._trigger_callbacks("after_clear")
        except Exception as e:
            success = False
            if self.policy == StoragePolicy.STRICT:
                raise StorageError(f"Failed to clear storage: {e}")
        finally:
            self.update_metrics("clear", success, time.time() - start_time)

    def get_size(self) -> int:
        """Get the total size of cold storage in bytes."""
        return sum(item["size"] for item in self.metadata.values())

    def get_keys(self) -> list[str]:
        """Get all keys in cold storage."""
        return list(self.metadata.keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        metrics = self.get_metrics()
        return {
            "total_items": len(self.metadata),
            "total_size": self.get_size(),
            "avg_item_size": self.get_size() / len(self.metadata) if self.metadata else 0,
            "hit_ratio": metrics.hits / (metrics.hits + metrics.misses) if metrics.hits + metrics.misses > 0 else 0,
            "avg_response_time": metrics.avg_response_time,
            "total_operations": metrics.total_operations,
            "total_errors": metrics.total_errors
        }

    def get_item_metadata(self, key: str) -> Optional[Dict]:
        """Get metadata for a specific item."""
        return self.metadata.get(key)

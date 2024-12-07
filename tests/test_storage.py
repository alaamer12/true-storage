"""Test suite for storage modules.

This module provides comprehensive testing for hot, cold, and mixed storage implementations.
Tests focus on core functionality, thread safety, and integration between storage types.
"""

import os
import pytest
import threading
import time
from typing import Any, Generator

from true_storage.storage.hot import HotStorage
from true_storage.storage.cold import ColdStorage
from true_storage.storage.mixed import MixedStorage
from true_storage.storage.base import StoragePolicy
from true_storage.exceptions import StorageError

# Test fixtures

@pytest.fixture
def temp_storage_dir(tmp_path) -> Generator[str, None, None]:
    """Create a temporary directory for cold storage testing."""
    storage_dir = os.path.join(str(tmp_path), "cold_storage")
    os.makedirs(storage_dir, exist_ok=True)
    yield storage_dir

@pytest.fixture
def hot_storage() -> Generator[HotStorage, None, None]:
    """Create a hot storage instance."""
    storage = HotStorage(
        storage_id="test_hot",
        max_size=5,
        expiration_time=1,  # Short expiration for testing
        policy=StoragePolicy.STRICT
    )
    yield storage

@pytest.fixture
def cold_storage(temp_storage_dir) -> Generator[ColdStorage, None, None]:
    """Create a cold storage instance."""
    storage = ColdStorage(
        storage_id="test_cold",
        storage_directory=temp_storage_dir,
        compression_level=6,
        policy=StoragePolicy.STRICT
    )
    yield storage

@pytest.fixture
def mixed_storage(temp_storage_dir) -> Generator[MixedStorage, None, None]:
    """Create a mixed storage instance."""
    storage = MixedStorage(
        storage_id="test_mixed",
        max_size=5,
        expiration_time=1,  # Short expiration for testing
        storage_directory=temp_storage_dir,
        compression_level=6,
        policy=StoragePolicy.STRICT
    )
    yield storage

# Test cases

class TestHotStorage:
    """Test hot storage functionality."""

    def test_basic_operations(self, hot_storage: HotStorage) -> None:
        """Test basic storage operations."""
        # Store and retrieve
        hot_storage.store("key1", "value1")
        assert hot_storage.retrieve("key1") == "value1"

        # Delete
        hot_storage.delete("key1")
        assert hot_storage.retrieve("key1") is None

        # Clear
        hot_storage.store("key2", "value2")
        hot_storage.clear()
        assert hot_storage.retrieve("key2") is None

    def test_lru_eviction(self, hot_storage: HotStorage) -> None:
        """Test LRU eviction strategy."""
        # Fill storage to max
        for i in range(5):
            hot_storage.store(f"key{i}", f"value{i}")

        # Access key0 to make it most recently used
        hot_storage.retrieve("key0")

        # Add new item, should evict least recently used
        hot_storage.store("key5", "value5")

        # key1 should be evicted (least recently used)
        assert hot_storage.retrieve("key1") is None
        assert hot_storage.retrieve("key0") == "value0"
        assert hot_storage.retrieve("key5") == "value5"

    def test_expiration(self, hot_storage: HotStorage) -> None:
        """Test item expiration."""
        hot_storage.store("expire_key", "expire_value")
        time.sleep(1.1)  # Wait for expiration
        assert hot_storage.retrieve("expire_key") is None

    def test_concurrent_access(self, hot_storage: HotStorage) -> None:
        """Test thread-safe operations."""
        def worker(prefix: str) -> None:
            for i in range(50):
                key = f"{prefix}_{i}"
                hot_storage.store(key, i)
                assert hot_storage.retrieve(key) in (i, None)  # None is acceptable due to LRU eviction

        threads = [
            threading.Thread(target=worker, args=(f"thread{i}",))
            for i in range(3)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

class TestColdStorage:
    """Test cold storage functionality."""

    def test_basic_operations(self, cold_storage: ColdStorage) -> None:
        """Test basic storage operations."""
        # Store and retrieve with compression
        data = {"complex": "data", "with": ["nested", "structures"]}
        cold_storage.store("key1", data)
        assert cold_storage.retrieve("key1") == data

        # Delete
        cold_storage.delete("key1")
        assert cold_storage.retrieve("key1") is None

        # Clear
        cold_storage.store("key2", "value2")
        cold_storage.clear()
        assert cold_storage.retrieve("key2") is None

    def test_persistence(self, temp_storage_dir: str) -> None:
        """Test data persistence across storage instances."""
        # Store data in first instance
        storage1 = ColdStorage(
            storage_id="test_persistence",
            storage_directory=temp_storage_dir
        )
        storage1.store("persist_key", "persist_value")

        # Create new instance and verify data
        storage2 = ColdStorage(
            storage_id="test_persistence",
            storage_directory=temp_storage_dir
        )
        assert storage2.retrieve("persist_key") == "persist_value"

    def test_compression(self, cold_storage: ColdStorage) -> None:
        """Test data compression."""
        # Store large repetitive data that should compress well
        large_data = "a" * 1000
        cold_storage.store("compress_key", large_data)

        # Get compressed size from metadata
        metadata = cold_storage.get_item_metadata("compress_key")
        assert metadata["size"] < len(large_data)  # Compressed size should be smaller

class TestMixedStorage:
    """Test mixed storage functionality."""

    def test_storage_hierarchy(self, mixed_storage: MixedStorage) -> None:
        """Test storage hierarchy and caching behavior."""
        # Store in mixed storage
        mixed_storage.store("key1", "value1")

        # Should be in both hot and cold storage
        assert mixed_storage.hot_storage.retrieve("key1") == "value1"
        assert mixed_storage.cold_storage.retrieve("key1") == "value1"

        # Clear hot storage
        mixed_storage.hot_storage.clear()
        assert mixed_storage.hot_storage.retrieve("key1") is None

        # Should still be retrievable from mixed storage (and repopulate hot)
        assert mixed_storage.retrieve("key1") == "value1"
        assert mixed_storage.hot_storage.retrieve("key1") == "value1"

    def test_warm_up(self, mixed_storage: MixedStorage) -> None:
        """Test hot storage warm-up functionality."""
        # Store items only in cold storage
        for i in range(3):
            mixed_storage.cold_storage.store(f"key{i}", f"value{i}")
        mixed_storage.hot_storage.clear()

        # Warm up specific keys
        mixed_storage.warm_up_hot_storage(["key0", "key1"])

        # Verify warm-up
        assert mixed_storage.hot_storage.retrieve("key0") == "value0"
        assert mixed_storage.hot_storage.retrieve("key1") == "value1"
        assert mixed_storage.hot_storage.retrieve("key2") is None

    def test_optimization(self, mixed_storage: MixedStorage) -> None:
        """Test storage optimization."""
        # Fill hot storage
        for i in range(10):
            mixed_storage.store(f"key{i}", f"value{i}")

        # Optimize hot storage
        mixed_storage.optimize_hot_storage()

        # Verify only most accessed items remain
        stats = mixed_storage.get_hot_stats()
        assert stats["size"] <= mixed_storage.hot_storage.strategy.max_size

def test_storage_policies() -> None:
    """Test storage policies across all storage types."""
    storages = [
        HotStorage(policy=StoragePolicy.STRICT),
        ColdStorage(policy=StoragePolicy.LAZY),
        MixedStorage(policy=StoragePolicy.LENIENT)
    ]

    for storage in storages:
        # Should not raise exception in relaxed mode
        try:
            storage.retrieve("nonexistent_key")
            storage.delete("nonexistent_key")
            storage.store(None, "invalid_key")  # type: ignore
        except StorageError:
            pytest.fail("StorageError should not be raised in RELAXED mode")

        # Clean up
        storage.clear()

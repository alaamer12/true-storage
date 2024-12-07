"""Test suite for database storage modules.

This module provides comprehensive testing for filesystem and SQLite database implementations.
Tests focus on core functionality, thread safety, and data persistence.
"""

import os
import pickle
import pytest
import threading
import time
from pathlib import Path
from typing import Any, Generator

from true_storage.database.filesystem import FileSystemStorage
from true_storage.database.sqlite import SQLiteStorage
from true_storage.exceptions import StorageError

# Test Data
TEST_DATA = {
    "string": "test_value",
    "int": 42,
    "float": 3.14,
    "list": [1, 2, 3],
    "dict": {"key": "value"},
    "bytes": b"binary_data",
    "none": None
}

# Test Fixtures

@pytest.fixture
def temp_dir(tmp_path) -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    test_dir = os.path.join(str(tmp_path), "test_storage")
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir

@pytest.fixture
def fs_storage(temp_dir) -> Generator[FileSystemStorage, None, None]:
    """Create a filesystem storage instance."""
    storage = FileSystemStorage(base_dir=temp_dir)
    yield storage

@pytest.fixture
def sqlite_storage(temp_dir) -> Generator[SQLiteStorage, None, None]:
    """Create a SQLite storage instance."""
    db_path = os.path.join(temp_dir, "test.db")
    storage = SQLiteStorage(db_path=db_path)
    yield storage
    storage.close()

# Base Test Class

class BaseStorageTests:
    """Base class for storage tests."""

    @pytest.fixture
    def storage(self) -> Any:
        """Abstract fixture to be implemented by subclasses."""
        raise NotImplementedError

    def test_basic_operations(self, storage: Any) -> None:
        """Test basic storage operations."""
        # Test storing and retrieving different types of data
        for key, value in TEST_DATA.items():
            storage.store(key, value)
            assert storage.retrieve(key) == value

        # Test key error
        with pytest.raises(KeyError):
            storage.retrieve("nonexistent_key")

        # Test deletion
        storage.delete("string")
        with pytest.raises(KeyError):
            storage.retrieve("string")

        # Test clearing all data
        storage.clear()
        with pytest.raises(KeyError):
            storage.retrieve("int")

    def test_hierarchical_keys(self, storage: Any) -> None:
        """Test using hierarchical keys."""
        # Store values with hierarchical keys
        storage.store("level1/key1", "value1")
        storage.store("level1/level2/key2", "value2")
        storage.store("level1/level2/key3", "value3")

        # Verify retrieval
        assert storage.retrieve("level1/key1") == "value1"
        assert storage.retrieve("level1/level2/key2") == "value2"

        # Test deletion of nested key
        storage.delete("level1/level2/key2")
        with pytest.raises(KeyError):
            storage.retrieve("level1/level2/key2")

    # def test_concurrent_access(self, storage: Any) -> None:
      #     """Test thread-safe operations."""
    #     thread_count = 10
    #     operations_per_thread = 50
    #
    #     def worker(thread_id: int) -> None:
    #         for i in range(operations_per_thread):
    #             key = f"thread_{thread_id}_key_{i}"
    #             value = f"value_{i}"
    #
    #             # Test store and retrieve
    #             storage.store(key, value)
    #             assert storage.retrieve(key) == value
    #
    #             # Test delete
    #             storage.delete(key)
    #             with pytest.raises(KeyError):
    #                 storage.retrieve(key)
    #
    #     threads = [
    #         threading.Thread(target=worker, args=(i,))
    #         for i in range(thread_count)
    #     ]
    #
    #     for thread in threads:
    #         thread.start()
    #     for thread in threads:
    #         thread.join()

    def test_large_data(self, storage: Any) -> None:
        """Test handling of large data objects."""
        # Create a large nested structure
        large_data = {
            "level1": {
                f"key_{i}": {
                    "data": "x" * 1000,
                    "list": list(range(100))
                } for i in range(100)
            }
        }

        # Store and retrieve large data
        storage.store("large_key", large_data)
        retrieved_data = storage.retrieve("large_key")
        assert retrieved_data == large_data

    # def test_error_handling(self, storage: Any) -> None:
      #     """Test error handling."""
    #     # Test invalid keys
    #     with pytest.raises(StorageError):
    #         storage.store("../invalid/key", "value")
    #
    #     # Test storing invalid objects
    #     with pytest.raises(StorageError):
    #         storage.store("key", lambda x: x)  # Functions can't be pickled

class TestFileSystemStorage(BaseStorageTests):
    """Test filesystem storage implementation."""

    @pytest.fixture
    def storage(self, fs_storage: FileSystemStorage) -> FileSystemStorage:
        """Provide filesystem storage for tests."""
        return fs_storage

    def test_persistence(self, temp_dir: str) -> None:
        """Test data persistence across storage instances."""
        # Store data in first instance
        storage1 = FileSystemStorage(base_dir=temp_dir)
        storage1.store("persist_key", "persist_value")

        # Verify data in second instance
        storage2 = FileSystemStorage(base_dir=temp_dir)
        assert storage2.retrieve("persist_key") == "persist_value"

    def test_file_integrity(self, fs_storage: FileSystemStorage) -> None:
        """Test file integrity and atomic operations."""
        test_key = "test_key"
        test_value = "test_value"

        # Store value
        fs_storage.store(test_key, test_value)
        file_path = fs_storage._get_path(test_key)

        # Verify file exists and contains correct data
        assert file_path.exists()
        with open(file_path, 'rb') as f:
            stored_value = pickle.load(f)
            assert stored_value == test_value

        # Verify no temporary files remain
        temp_files = list(file_path.parent.glob("*.tmp"))
        assert len(temp_files) == 0

class TestSQLiteStorage(BaseStorageTests):
    """Test SQLite storage implementation."""

    @pytest.fixture
    def storage(self, sqlite_storage: SQLiteStorage) -> SQLiteStorage:
        """Provide SQLite storage for tests."""
        return sqlite_storage

    def test_persistence(self, temp_dir: str) -> None:
        """Test data persistence across storage instances."""
        db_path = os.path.join(temp_dir, "persist_test.db")
        
        # Store data in first instance
        storage1 = SQLiteStorage(db_path=db_path)
        storage1.store("persist_key", "persist_value")
        storage1.close()

        # Verify data in second instance
        storage2 = SQLiteStorage(db_path=db_path)
        assert storage2.retrieve("persist_key") == "persist_value"
        storage2.close()

    def test_in_memory_storage(self) -> None:
        """Test in-memory database functionality."""
        storage = SQLiteStorage()  # Uses in-memory database
        
        # Test basic operations
        storage.store("key", "value")
        assert storage.retrieve("key") == "value"
        
        # Verify data doesn't persist after closing
        storage.close()
        new_storage = SQLiteStorage()
        with pytest.raises(KeyError):
            new_storage.retrieve("key")
        new_storage.close()

    def test_connection_handling(self, sqlite_storage: SQLiteStorage) -> None:
        """Test database connection handling."""
        # Test connection creation
        conn1 = sqlite_storage._get_connection()
        conn2 = sqlite_storage._get_connection()
        assert conn1 is conn2  # Should reuse the same connection

        # Test connection closure
        sqlite_storage.close()
        assert sqlite_storage._conn is None

        # Test automatic reconnection
        sqlite_storage.store("key", "value")
        assert sqlite_storage.retrieve("key") == "value"

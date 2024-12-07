"""Test suite for the session store module."""

import tempfile
import time
from pathlib import Path

import pytest

from true_storage.session import (
    SessionStore,
    SessionStoreConfig,
    SessionStatus,
    StorageError
)


@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for session persistence."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="function")
def session_store(temp_dir, request):
    """Create a session store instance with test configuration."""
    config = SessionStoreConfig(
        max_size=3,  # Small size to test LRU eviction
        expiration_time=2,  # Short expiration for testing
        cleanup_interval=0.5,  # Fast cleanup for testing
        persistence_path=str(Path(temp_dir) / "sessions.json"),
        backup_interval=0.5,  # Fast backup for testing
        enable_logging=False  # Disable logging for tests
    )
    store = SessionStore(config)
    
    def cleanup():
        store.stop()  # Ensure store is stopped after each test
    request.addfinalizer(cleanup)
    
    return store


def test_basic_operations(session_store):
    """Test basic set/get operations."""
    session_store.set("key1", "value1")
    assert session_store.get("key1") == "value1"
    
    metadata = session_store.get_metadata("key1")
    assert metadata.status == SessionStatus.ACTIVE
    assert metadata.access_count == 1


def test_expiration(session_store):
    """Test session expiration."""
    session_store.set("key1", "value1")
    assert session_store.get("key1") == "value1"
    
    # Wait for expiration
    time.sleep(2.5)  # Longer than expiration_time
    assert session_store.get("key1") is None


# def test_lru_eviction(session_store):
#     """Test LRU eviction when max size is reached."""
#     # Fill store to max size
#     session_store.set("key1", "value1")
#     session_store.set("key2", "value2")
#     session_store.set("key3", "value3")
#
#     # Access key1 to make it most recently used
#     session_store.get("key1")
#
#     # Add new key, should evict key2 (least recently used)
#     session_store.set("key4", "value4")
#
#     assert session_store.get("key1") == "value1"  # Most recently used
#     assert session_store.get("key2") is None  # Evicted
#     assert session_store.get("key3") == "value3"  # Not evicted
#     assert session_store.get("key4") == "value4"  # Newly added


def test_persistence(temp_dir):
    """Test session persistence and restoration."""
    config = SessionStoreConfig(
        max_size=10,
        expiration_time=10,  # Longer expiration for persistence test
        persistence_path=str(Path(temp_dir) / "sessions.json"),
        backup_interval=0.5,  # Fast backup for testing
        cleanup_interval=0.5,
        enable_logging=False
    )
    
    # Create and populate first store
    store1 = SessionStore(config)
    try:
        store1.set("key1", "value1")
        store1.set("key2", "value2")
        time.sleep(1)  # Wait for backup
    finally:
        store1.stop()
    
    # Create new store, should restore sessions
    store2 = SessionStore(config)
    try:
        assert store2.get("key1") == "value1"
        assert store2.get("key2") == "value2"
    finally:
        store2.stop()


# def test_concurrent_access(session_store):
  #     """Test thread safety with concurrent access."""
#     def writer():
#         for i in range(10):  # Reduced iterations
#             session_store.set(f"key{i}", f"value{i}")
#             time.sleep(0.01)
#
#     def reader():
#         for i in range(10):  # Reduced iterations
#             _ = session_store.get(f"key{i}")
#             time.sleep(0.01)
#
#     threads = [
#         threading.Thread(target=writer),
#         threading.Thread(target=reader)
#     ]
#
#     for t in threads:
#         t.start()
#
#     for t in threads:
#         t.join(timeout=1.0)
#
#     # Verify some data was written
#     assert any(session_store.get(f"key{i}") == f"value{i}" for i in range(10))


def test_locking(session_store):
    """Test session locking mechanism."""
    session_store.set("key1", "value1")
    
    # Lock the session
    assert session_store.lock("key1", duration=1)
    
    # Verify locked status
    metadata = session_store.get_metadata("key1")
    assert metadata.status == SessionStatus.LOCKED
    
    # Attempt to access locked session
    with pytest.raises(StorageError):
        session_store.get("key1")
    
    # Wait for lock to expire
    time.sleep(1.5)
    
    # Should be accessible now
    assert session_store.get("key1") == "value1"


def test_dict_interface(session_store):
    """Test dictionary-like interface."""
    session_store["key1"] = "value1"
    assert session_store["key1"] == "value1"
    assert "key1" in session_store
    assert len(session_store) == 1
    
    del session_store["key1"]
    assert "key1" not in session_store
    
    with pytest.raises(KeyError):
        _ = session_store["nonexistent"]

"""Test suite for the session store module."""

import tempfile
import threading
import time
from pathlib import Path

import pytest
from freezegun import freeze_time

from true_storage.session import (
    SessionStore,
    SessionStoreConfig,
    SessionStatus,
    StorageError
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for session persistence."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def session_store(temp_dir):
    """Create a session store instance with test configuration."""
    config = SessionStoreConfig(
        max_size=3,  # Small size to test LRU eviction
        expiration_time=60,  # 1 minute expiration
        cleanup_interval=1,  # Fast cleanup for testing
        persistence_path=str(Path(temp_dir) / "sessions.json"),
        backup_interval=1,  # Fast backup for testing
        enable_logging=False  # Disable logging for tests
    )
    store = SessionStore(config)
    yield store
    store.stop()  # Cleanup after tests


def test_session_lifecycle(session_store):
    """Test basic session operations and expiration."""
    with freeze_time("2023-01-01 12:00:00"):
        # Store a session
        session_store.set("key1", "value1")
        assert session_store.get("key1") == "value1"
        
        # Check metadata
        metadata = session_store.get_metadata("key1")
        assert metadata.status == SessionStatus.ACTIVE
        assert metadata.access_count == 1
        
        # Move time forward past expiration
        with freeze_time("2023-01-01 12:01:01"):
            # Wait for cleanup thread
            time.sleep(2)
            assert "key1" not in session_store
            assert session_store.get("key1") is None


def test_lru_eviction(session_store):
    """Test LRU eviction when max size is reached."""
    # Fill store to max size
    session_store.set("key1", "value1")
    session_store.set("key2", "value2")
    session_store.set("key3", "value3")
    
    # Access key1 to make it most recently used
    session_store.get("key1")
    
    # Add new key, should evict key2 (least recently used)
    session_store.set("key4", "value4")
    
    assert "key1" in session_store  # Most recently used
    assert "key2" not in session_store  # Evicted
    assert "key3" in session_store  # Not evicted
    assert "key4" in session_store  # Newly added


def test_persistence(temp_dir):
    """Test session persistence and restoration."""
    config = SessionStoreConfig(
        max_size=10,
        persistence_path=str(Path(temp_dir) / "sessions.json"),
        backup_interval=1
    )
    
    # Create and populate first store
    store1 = SessionStore(config)
    store1.set("key1", "value1")
    store1.set("key2", "value2")
    
    # Wait for backup
    time.sleep(2)
    store1.stop()
    
    # Create new store, should restore sessions
    store2 = SessionStore(config)
    assert store2.get("key1") == "value1"
    assert store2.get("key2") == "value2"
    store2.stop()


def test_concurrent_access(session_store):
    """Test thread safety with concurrent access."""
    def writer_thread():
        for i in range(100):
            session_store.set(f"key{i}", f"value{i}")
            time.sleep(0.01)  # Small delay to increase contention

    def reader_thread():
        for i in range(100):
            _ = session_store.get(f"key{i}")
            time.sleep(0.01)

    # Start concurrent threads
    writer = threading.Thread(target=writer_thread)
    reader = threading.Thread(target=reader_thread)
    
    writer.start()
    reader.start()
    
    writer.join()
    reader.join()
    
    # Verify no data corruption
    for i in range(100):
        value = session_store.get(f"key{i}")
        if value is not None:  # Some keys might be evicted
            assert value == f"value{i}"


def test_session_locking(session_store):
    """Test session locking mechanism."""
    session_store.set("key1", "value1")
    
    # Lock the session
    assert session_store.lock("key1", duration=2)
    
    # Verify locked status
    metadata = session_store.get_metadata("key1")
    assert metadata.status == SessionStatus.LOCKED
    
    # Attempt to access locked session
    with pytest.raises(StorageError):
        session_store.get("key1")
    
    # Wait for lock to expire
    time.sleep(3)
    
    # Should be accessible now
    assert session_store.get("key1") == "value1"
    metadata = session_store.get_metadata("key1")
    assert metadata.status == SessionStatus.ACTIVE


def test_dict_like_interface(session_store):
    """Test dictionary-like interface."""
    # Test __setitem__
    session_store["key1"] = "value1"
    
    # Test __getitem__
    assert session_store["key1"] == "value1"
    
    # Test __contains__
    assert "key1" in session_store
    
    # Test __len__
    assert len(session_store) == 1
    
    # Test __delitem__
    del session_store["key1"]
    assert "key1" not in session_store
    
    # Test KeyError
    with pytest.raises(KeyError):
        _ = session_store["nonexistent"]

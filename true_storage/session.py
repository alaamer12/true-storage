"""Session management module for in-memory data storage with persistence capabilities.

This module provides a robust implementation of a session store with features like
expiration, cleanup, and persistence. It offers thread-safe operations and LRU (Least
Recently Used) eviction strategy.

Classes:
    SessionStatus: Enumeration of possible session states (ACTIVE, EXPIRED, LOCKED).
    SessionMetadata: Data class containing metadata for session entries.
    SessionStoreConfig: Configuration class for SessionStore settings.
    SessionStore: Main class implementing the session storage functionality.

Functions:
    None 

Types:
    None

Exceptions:
    StorageError: Raised when storage operations fail

Key Features:
    - Thread-safe operations with lock mechanism
    - Automatic session expiration and cleanup
    - LRU (Least Recently Used) eviction strategy
    - Session persistence to disk with atomic writes
    - Session locking for exclusive access
    - Dict-like interface with familiar operations
    - Configurable logging
    - Background cleanup and backup processes
"""

import json
import logging
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Dict, Iterator, List

from true_storage.exceptions import StorageError

__all__ = [
    'SessionStatus',
    'SessionMetadata',
    'SessionStoreConfig',
    'SessionStore',
    'StorageError'
]

def __dir__() -> List[str]:
    return sorted(__all__)


class SessionStatus(Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    LOCKED = "locked"


@dataclass
class SessionMetadata:
    """Metadata for session entries."""
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    status: SessionStatus = SessionStatus.ACTIVE
    lock_expiry: Optional[float] = None


@dataclass
class SessionStoreConfig:
    """Configuration for SessionStore."""
    max_size: int = 1000
    expiration_time: int = 3600  # 1 hour
    cleanup_interval: int = 60  # 1 minute
    persistence_path: Optional[str] = None  # Path for session persistence
    backup_interval: int = 300  # 5 minutes
    max_lock_time: int = 30  # Maximum lock duration in seconds
    enable_logging: bool = True
    log_level: int = logging.INFO


class SessionStore:
    """A robust and thread-safe in-memory session store with expiration, LRU eviction, and persistence."""

    def __init__(self, config: SessionStoreConfig = None):
        self.config = config or SessionStoreConfig()
        self._store: OrderedDict = OrderedDict()
        self._metadata: Dict[Any, SessionMetadata] = {}
        self._lock = threading.Lock()
        self._running = True
        self._threads_initialized = False
        
        # Setup logging
        if self.config.enable_logging:
            self._setup_logging()
        
        # Initialize stop events
        self._stop_cleanup = threading.Event()
        self._cleanup_thread = None
        
        self._stop_backup = None
        self._backup_thread = None
        
        # Start background threads
        self._start_background_threads()

    def _start_background_threads(self):
        """Initialize and start background threads."""
        if self._threads_initialized:
            return
            
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_expired_sessions,
            daemon=True,
            name="cleanup-thread"
        )
        self._cleanup_thread.start()
        
        # Start backup thread if persistence is enabled
        if self.config.persistence_path:
            self._stop_backup = threading.Event()
            self._backup_thread = threading.Thread(
                target=self._backup_sessions,
                daemon=True,
                name="backup-thread"
            )
            self._backup_thread.start()
            self._restore_sessions()
        
        self._threads_initialized = True

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        self.logger = logging.getLogger("SessionStore")
        self.logger.setLevel(self.config.log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def set(self, key: Any, value: Any, expiration: Optional[int] = None) -> None:
        """Set a session key to a value with optional custom expiration."""
        with self._lock:
            try:
                if len(self._store) >= self.config.max_size:
                    self._evict_lru_session()
                
                timestamp = time.time()
                self._store[key] = value
                self._metadata[key] = SessionMetadata(
                    created_at=timestamp,
                    last_accessed=timestamp
                )
                
                if self.config.enable_logging:
                    self.logger.info(f"Set key: {key} at {datetime.fromtimestamp(timestamp)}")
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.error(f"Failed to set value for key {key}: {e}")
                raise StorageError(f"Failed to set value: {e}")

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        """Retrieve a session value by key with metadata update."""
        with self._lock:
            try:
                if key not in self._store:
                    return default

                metadata = self._metadata[key]
                current_time = time.time()
                
                # Check lock status
                if metadata.status == SessionStatus.LOCKED:
                    if current_time < metadata.lock_expiry:
                        if self.config.enable_logging:
                            self.logger.warning(f"Attempted to access locked key: {key}")
                        raise StorageError(f"Key {key} is locked")
                    metadata.status = SessionStatus.ACTIVE
                    metadata.lock_expiry = None

                # Check expiration
                if current_time - metadata.created_at > self.config.expiration_time:
                    self.delete(key)
                    return default

                # Update metadata
                metadata.last_accessed = current_time
                metadata.access_count += 1
                
                if self.config.enable_logging:
                    self.logger.debug(f"Accessed key: {key} (access count: {metadata.access_count})")
                
                return self._store[key]
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.error(f"Failed to get value for key {key}: {e}")
                raise StorageError(f"Failed to get value: {e}")

    def lock(self, key: Any, duration: Optional[int] = None) -> bool:
        """Lock a session key for exclusive access."""
        with self._lock:
            if key not in self._store:
                return False
            
            lock_time = duration or self.config.max_lock_time
            metadata = self._metadata[key]
            metadata.status = SessionStatus.LOCKED
            metadata.lock_expiry = time.time() + lock_time
            
            if self.config.enable_logging:
                self.logger.info(f"Locked key: {key} for {lock_time} seconds")
            return True

    def unlock(self, key: Any) -> bool:
        """Unlock a session key."""
        with self._lock:
            if key not in self._store:
                return False
            
            metadata = self._metadata[key]
            if metadata.status == SessionStatus.LOCKED:
                metadata.status = SessionStatus.ACTIVE
                metadata.lock_expiry = None
                
                if self.config.enable_logging:
                    self.logger.info(f"Unlocked key: {key}")
                return True
            return False

    def _evict_lru_session(self) -> None:
        """Evict the least recently used session."""
        lru_key = min(
            self._metadata.items(),
            key=lambda x: x[1].last_accessed
        )[0]
        self.delete(lru_key)
        if self.config.enable_logging:
            self.logger.info(f"Evicted LRU key: {lru_key}")

    def get_metadata(self, key: Any) -> Optional[SessionMetadata]:
        """Get metadata for a session key."""
        with self._lock:
            return self._metadata.get(key)

    def get_status(self, key: Any) -> Optional[SessionStatus]:
        """Get the status of a session key."""
        metadata = self.get_metadata(key)
        return metadata.status if metadata else None

    def _backup_sessions(self) -> None:
        """Periodically backup sessions to disk if persistence is enabled."""
        while self._running and not self._stop_backup.is_set():
            try:
                if not self.config.persistence_path:
                    break
                self._save_to_disk()
                if self.config.enable_logging:
                    self.logger.debug("Sessions backed up successfully")
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.error(f"Failed to backup sessions: {e}")
                if not self._running:
                    break
            
            # Use shorter intervals when stopping
            interval = 0.1 if not self._running else self.config.backup_interval
            if self._stop_backup.wait(interval):
                break

    def _save_to_disk(self) -> None:
        """Save sessions to disk."""
        if not self.config.persistence_path:
            return
            
        with self._lock:
            backup_data = {
                'timestamp': time.time(),
                'sessions': {
                    str(key): {
                        'value': self._store[key],
                        'metadata': {
                            'created_at': self._metadata[key].created_at,
                            'last_accessed': self._metadata[key].last_accessed,
                            'access_count': self._metadata[key].access_count,
                            'status': self._metadata[key].status.value,
                            'lock_expiry': self._metadata[key].lock_expiry
                        }
                    }
                    for key in self._store
                }
            }
            
            path = Path(self.config.persistence_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first
            temp_path = path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(backup_data, f)
            
            # Atomic rename
            temp_path.replace(path)

    def _restore_sessions(self) -> None:
        """Restore sessions from disk on initialization."""
        if not self.config.persistence_path:
            return
            
        try:
            path = Path(self.config.persistence_path)
            if not path.exists():
                return
                
            with open(path, 'r') as f:
                backup_data = json.load(f)
                
            current_time = time.time()
            for key, data in backup_data['sessions'].items():
                if current_time - data['metadata']['created_at'] <= self.config.expiration_time:
                    self._store[key] = data['value']
                    self._metadata[key] = SessionMetadata(
                        created_at=data['metadata']['created_at'],
                        last_accessed=data['metadata']['last_accessed'],
                        access_count=data['metadata']['access_count'],
                        status=SessionStatus(data['metadata']['status']),
                        lock_expiry=data['metadata']['lock_expiry']
                    )
            
            if self.config.enable_logging:
                self.logger.info(f"Restored {len(self._store)} sessions from disk")
        except Exception as e:
            if self.config.enable_logging:
                self.logger.error(f"Failed to restore sessions: {e}")

    def stop(self) -> None:
        """Stop all background threads and perform final backup."""
        if not self._running or not self._threads_initialized:
            return
        
        self._running = False
        
        # Set stop events
        self._stop_cleanup.set()
        if self._stop_backup:
            self._stop_backup.set()
        
        # Final backup with short timeout
        if self.config.persistence_path:
            try:
                self._save_to_disk()
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.error(f"Failed to perform final backup: {e}")
        
        # Join threads with short timeouts
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=0.5)
            if self._cleanup_thread.is_alive():
                if self.config.enable_logging:
                    self.logger.warning("Cleanup thread did not stop gracefully")
        
        if self._backup_thread:
            self._backup_thread.join(timeout=0.5)
            if self._backup_thread.is_alive():
                if self.config.enable_logging:
                    self.logger.warning("Backup thread did not stop gracefully")
        
        if self.config.enable_logging:
            self.logger.info("Session store stopped")
        
        self._threads_initialized = False

    def __del__(self):
        """Ensure all threads are stopped and final backup is performed."""
        try:
            if getattr(self, '_running', False) and getattr(self, '_threads_initialized', False):
                self.stop()
        except Exception as e:
            if hasattr(self, 'logger') and self.config.enable_logging:
                self.logger.error(f"Error during cleanup: {e}")

    def delete(self, key: Any) -> bool:
        """Delete a session key. Returns True if the key was deleted, False if not found."""
        with self._lock:
            try:
                if key in self._store:
                    del self._store[key]
                    del self._metadata[key]
                    return True
                return False
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.error(f"Failed to delete value for key {key}: {e}")
                raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        """Clear all sessions."""
        with self._lock:
            try:
                self._store.clear()
                self._metadata.clear()
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.error(f"Failed to clear sessions: {e}")
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
        while self._running and not self._stop_cleanup.is_set():
            try:
                with self._lock:
                    if not self._running:
                        break
                    current_time = time.time()
                    expired_keys = [
                        key for key, metadata in self._metadata.items()
                        if current_time - metadata.created_at > self.config.expiration_time
                    ]
                    for key in expired_keys:
                        if not self._running:
                            break
                        self.delete(key)
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.error(f"Failed to cleanup sessions: {e}")
                if not self._running:
                    break
            
            # Use shorter intervals when stopping
            interval = 0.1 if not self._running else self.config.cleanup_interval
            if self._stop_cleanup.wait(interval):
                break

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
                1 for metadata in self._metadata.values()
                if current_time - metadata.created_at <= self.config.expiration_time
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

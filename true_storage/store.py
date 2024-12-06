from __future__ import annotations

import configparser
import functools
import json
import os
import pickle
import shutil
import sqlite3
import tempfile
import threading
import time
import zlib
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import (Callable, Any, List, Dict,
                    Optional, Union, Literal,
                    Tuple, NoReturn, Iterator)

import dotenv
import redis

PathLike = Optional[Union[str, os.PathLike]]
EnvPath = Union[PathLike, Dict,
    # JsonType
NoReturn]


class EnvError(Exception):
    """Exception raised for environment errors."""
    pass


class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass


class StorageConnectionError(StorageError):
    """Raised when a storage connection fails."""
    pass


class FileSystemStorage:
    """File system-based storage implementation."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or tempfile.gettempdir()) / "checkpoints"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _get_path(self, key: str) -> Path:
        """Get a full path for a key."""
        return self.base_dir / f"{key}.pkl"

    def store(self, key: str, value: Any) -> None:
        with self._lock:
            path = self._get_path(key)
            temp_path = path.with_suffix('.tmp')
            try:
                with open(temp_path, 'wb') as f:
                    pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
                temp_path.replace(path)
            except Exception as e:
                if temp_path.exists():
                    temp_path.unlink()
                raise StorageError(f"Failed to store value: {e}")

    def retrieve(self, key: str) -> Any:
        with self._lock:
            path = self._get_path(key)
            try:
                with open(path, 'rb') as f:
                    return pickle.load(f)
            except FileNotFoundError:
                raise KeyError(f"No value found for key: {key}")
            except Exception as e:
                raise StorageError(f"Failed to retrieve value: {e}")

    def delete(self, key: str) -> None:
        with self._lock:
            path = self._get_path(key)
            try:
                path.unlink(missing_ok=True)
            except Exception as e:
                raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        with self._lock:
            try:
                shutil.rmtree(self.base_dir)
                self.base_dir.mkdir(parents=True)
            except Exception as e:
                raise StorageError(f"Failed to clear storage: {e}")

    def clone(self) -> 'FileSystemStorage':
        new_storage = FileSystemStorage(tempfile.mkdtemp())
        with self._lock:
            try:
                shutil.copytree(self.base_dir, new_storage.base_dir, dirs_exist_ok=True)
                return new_storage
            except Exception as e:
                raise StorageError(f"Failed to clone storage: {e}")


# noinspection SqlResolve
class SQLiteStorage:
    """SQLite-based storage implementation."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or ":memory:"
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self) -> None:
        with self._lock, sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    item_k TEXT PRIMARY KEY,
                    value BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def store(self, key: str, value: Any) -> None:
        with self._lock, sqlite3.connect(self.db_path) as conn:
            try:
                binary_data = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                conn.execute(
                    "INSERT OR REPLACE INTO checkpoints (key, value) VALUES (?, ?)",
                    (key, binary_data)
                )
            except Exception as e:
                raise StorageError(f"Failed to store value: {e}")

    def retrieve(self, key: str) -> Any:
        with self._lock, sqlite3.connect(self.db_path) as conn:
            try:
                result = conn.execute(
                    "SELECT value FROM checkpoints WHERE item_k = ?",
                    (key,)
                ).fetchone()
                if result is None:
                    raise KeyError(f"No value found for key: {key}")
                return pickle.loads(result[0])
            except Exception as e:
                raise StorageError(f"Failed to retrieve value: {e}")

    def delete(self, key: str) -> None:
        with self._lock, sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("DELETE FROM checkpoints WHERE item_k = ?", (key,))
            except Exception as e:
                raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        with self._lock, sqlite3.connect(self.db_path) as conn:
            try:
                # noinspection SqlWithoutWhere
                conn.execute("DELETE FROM checkpoints")
            except Exception as e:
                raise StorageError(f"Failed to clear storage: {e}")

    def clone(self) -> 'SQLiteStorage':
        new_storage = SQLiteStorage(":memory:")
        with self._lock, \
                sqlite3.connect(self.db_path) as source_conn, \
                sqlite3.connect(new_storage.db_path) as dest_conn:
            try:
                source_conn.backup(dest_conn)
                return new_storage
            except Exception as e:
                raise StorageError(f"Failed to clone storage: {e}")


class RedisStorage:
    """Redis-based storage implementation."""

    def __init__(
            self,
            host: str = 'localhost',
            port: int = 6379,
            db: int = 0,
            prefix: str = 'checkpoint:'
    ):
        self.prefix = prefix
        self._lock = threading.RLock()
        try:
            self.redis = redis.Redis(host=host, port=port, db=db)
            self.redis.ping()
        except redis.ConnectionError as e:
            raise StorageConnectionError(f"Failed to connect to Redis: {e}")

    def _get_key(self, key: str) -> str:
        """Get prefixed key for Redis."""
        return f"{self.prefix}{key}"

    def store(self, key: str, value: Any) -> None:
        with self._lock:
            try:
                binary_data = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                self.redis.set(self._get_key(key), binary_data)
            except Exception as e:
                raise StorageError(f"Failed to store value: {e}")

    def retrieve(self, key: str) -> Any:
        with self._lock:
            try:
                data = self.redis.get(self._get_key(key))
                if data is None:
                    raise KeyError(f"No value found for key: {key}")
                return pickle.loads(data)
            except Exception as e:
                raise StorageError(f"Failed to retrieve value: {e}")

    def delete(self, key: str) -> None:
        with self._lock:
            try:
                self.redis.delete(self._get_key(key))
            except Exception as e:
                raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        with self._lock:
            try:
                keys = self.redis.keys(f"{self.prefix}*")
                if keys:
                    self.redis.delete(*keys)
            except Exception as e:
                raise StorageError(f"Failed to clear storage: {e}")

    def clone(self) -> 'RedisStorage':
        new_storage = RedisStorage(prefix=f"{self.prefix}clone:")
        with self._lock:
            try:
                keys = self.redis.keys(f"{self.prefix}*")
                pipeline = self.redis.pipeline()
                for key in keys:
                    value = self.redis.get(key)
                    new_key = key.replace(
                        self.prefix.encode(),
                        new_storage.prefix.encode()
                    )
                    pipeline.set(new_key, value)
                pipeline.execute()
                return new_storage
            except Exception as e:
                raise StorageError(f"Failed to clone storage: {e}")


class ColdStorage:
    def __init__(self, storage_directory='cold_storage', metadata_file='metadata.json'):
        self.storage_directory = storage_directory
        self.metadata_file = metadata_file
        self.metadata = {}
        self._load_metadata()
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Create the storage directory if it does not exist."""
        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)

    def _load_metadata(self):
        """Load metadata from a JSON file."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as file:
                self.metadata = json.load(file)

    def _save_metadata(self):
        """Save metadata to a JSON file."""
        with open(self.metadata_file, 'w') as file:
            json.dump(self.metadata, file)

    @staticmethod
    def _compress_data(data):
        """Compress data using zlib."""
        return zlib.compress(pickle.dumps(data))

    @staticmethod
    def _decompress_data(compressed_data):
        """Decompress data using zlib."""
        return pickle.loads(zlib.decompress(compressed_data))

    def store(self, key, value):
        """Store an item in cold storage with metadata."""
        filename = os.path.join(self.storage_directory, f"{key}.bin")
        compressed_data = self._compress_data(value)

        with open(filename, 'wb') as file:
            file.write(compressed_data)

        self.metadata[key] = {
            'filename': f"{key}.bin",
            'stored_at': datetime.now().isoformat()
        }
        self._save_metadata()

    def clone(self):
        """Return a copy of the cold storage with the same data."""
        # TODO: Implement this

    def retrieve(self, key):
        """Retrieve an item from cold storage."""
        if key in self.metadata:
            filename = os.path.join(self.storage_directory, self.metadata[key]['filename'])
            with open(filename, 'rb') as file:
                compressed_data = file.read()
                return self._decompress_data(compressed_data)
        return None

    def delete(self, key):
        """Delete an item from cold storage."""
        if key in self.metadata:
            filename = os.path.join(self.storage_directory, self.metadata[key]['filename'])
            if os.path.exists(filename):
                os.remove(filename)
            del self.metadata[key]
            self._save_metadata()

    def clear(self):
        """Clear all items from cold storage."""
        for filename in os.listdir(self.storage_directory):
            file_path = os.path.join(self.storage_directory, filename)
            os.remove(file_path)
        self.metadata.clear()
        self._save_metadata()


class HotStorage:
    def __init__(self, max_size=100, expiration_time=300):
        self.data = OrderedDict()  # Maintains insertion order
        self.max_size = max_size
        self.expiration_time = expiration_time  # Time in seconds
        self.lock = threading.Lock()  # For thread-safe access

    def _remove_expired_items(self):
        """Remove expired items from storage."""
        current_time = time.time()
        keys_to_delete = [key for key, (value, timestamp) in self.data.items() if
                          current_time - timestamp > self.expiration_time]
        for key in keys_to_delete:
            del self.data[key]

    def store(self, key, value):
        """Store an item in hot storage with a timestamp."""
        with self.lock:
            self._remove_expired_items()  # Clean up expired items
            if key in self.data:
                del self.data[key]  # Remove existing key to reinsert (to maintain order)
            self.data[key] = (value, time.time())  # Store value with timestamp
            if len(self.data) > self.max_size:
                self.data.popitem(last=False)  # Remove oldest item if max size exceeded

    def retrieve(self, key):
        """Retrieve an item from hot storage."""
        with self.lock:
            self._remove_expired_items()  # Clean up expired items
            item = self.data.get(key, None)
            return item[0] if item else None

    def delete(self, key):
        """Delete an item from hot storage."""
        with self.lock:
            if key in self.data:
                del self.data[key]

    def clear(self):
        """Clear all items from hot storage."""
        with self.lock:
            self.data.clear()

    def clone(self):
        """Return a copy of the hot storage with the same data."""
        # TODO: Implement this


class MixedStorage:
    def __init__(self, max_size=100, expiration_time=300):
        self.hot_storage = HotStorage(max_size, expiration_time)
        self.cold_storage = ColdStorage()
        self._lock = threading.Lock()

    def store_session(self, session_id, session_data):
        with self._lock:
            self.hot_storage.store(session_id, session_data)
            self.cold_storage.store(session_id, session_data)

    def retrieve_session(self, session_id):
        with self._lock:
            session_data = self.hot_storage.retrieve(session_id)
            if session_data is None:
                session_data = self.cold_storage.retrieve(session_id)
            return session_data

    def delete_session(self, session_id):
        with self._lock:
            self.hot_storage.delete(session_id)
            self.cold_storage.delete(session_id)

    def clear_storage(self):
        with self._lock:
            self.hot_storage.clear()
            self.cold_storage.clear()

    def __del__(self):
        self.clear_storage()

    def __repr__(self):
        return f"{self.__class__.__name__}(max_size={self.hot_storage.max_size}, expiration_time={self.hot_storage.expiration_time})"

    def __str__(self):
        return self.__repr__()


@dataclass(kw_only=True)
class SessionStoreConfig:
    max_size: int = 1000
    expiration_time: int = 3600  # seconds
    cleanup_interval: int = 60  # seconds


@dataclass
class SessionStore:
    """A robust and thread-safe in-memory session store with expiration and LRU eviction."""

    config: SessionStoreConfig = field(default_factory=SessionStoreConfig)
    _store: OrderedDict = field(init=False, default_factory=OrderedDict)
    _lock: threading.Lock = field(init=False, default_factory=threading.Lock)
    _stop_cleanup: threading.Event = field(init=False, default_factory=threading.Event)
    _cleanup_thread: threading.Thread = field(init=False)

    def __post_init__(self):
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        self._cleanup_thread.start()

    def set(self, key: Any, value: Any) -> None:
        """Set a session key to a value with the current timestamp."""
        with self._lock:
            current_time = time.time()
            if key in self._store:
                del self._store[key]
            elif len(self._store) >= self.config.max_size:
                evicted_key, _ = self._store.popitem(last=False)  # Evict LRU item
                print(f"Evicted key due to max_size limit: {evicted_key}")
            self._store[key] = (value, current_time + self.config.expiration_time)
            print(f"Set key: {key} with expiration at {current_time + self.config.expiration_time}")

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        """Retrieve a session value by key. Returns default if key is not found or expired."""
        with self._lock:
            item = self._store.get(key)
            if item:
                value, expire_at = item
                if expire_at >= time.time():
                    # Move the key to the end to mark it as recently used
                    self._store.move_to_end(key)
                    print(f"Accessed key: {key}")
                    return value
                else:
                    # Item has expired
                    del self._store[key]
                    print(f"Expired key removed: {key}")
            return default

    def delete(self, key: Any) -> bool:
        """Delete a session key. Returns True if the key was deleted, False if not found."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                print(f"Deleted key: {key}")
                return True
            print(f"Attempted to delete non-existent key: {key}")
            return False

    def clear(self) -> None:
        """Clear all sessions."""
        with self._lock:
            self._store.clear()
            print("Cleared all sessions.")

    def keys(self) -> Iterator[Any]:
        """Return an iterator over the session keys."""
        with self._lock:
            return iter(self._store.keys())

    def values(self) -> Iterator[Any]:
        """Return an iterator over the session values."""
        with self._lock:
            return (value for value, _ in self._store.values())

    def items(self) -> Iterator[Tuple[Any, Any]]:
        """Return an iterator over the session items (key, value)."""
        with self._lock:
            return ((key, value) for key, (value, expire_at) in self._store.items())

    def _cleanup_expired_sessions(self) -> None:
        """Background thread method to clean up expired sessions periodically."""
        while not self._stop_cleanup.is_set():
            with self._lock:
                current_time = time.time()
                keys_to_delete = [key for key, (_, expire_at) in self._store.items() if expire_at < current_time]
                for key in keys_to_delete:
                    del self._store[key]
                    print(f"Cleanup thread removed expired key: {key}")
            self._stop_cleanup.wait(self.config.cleanup_interval)

    def stop_cleanup(self) -> None:
        """Stop the background cleanup thread."""
        self._stop_cleanup.set()
        self._cleanup_thread.join()
        print("Cleanup thread stopped.")

    def __del__(self):
        """Ensure the cleanup thread is stopped when the instance is deleted."""
        self.stop_cleanup()

    def __setitem__(self, key: Any, value: Any) -> None:
        """Enable dict-like setting of items."""
        self.set(key, value)

    def __getitem__(self, key: Any) -> Any:
        """Enable dict-like getting of items."""
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result

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
            return len(self._store)

    def __repr__(self) -> str:
        with self._lock:
            return (f"{self.__class__.__name__}(max_size={self.config.max_size}, "
                    f"expiration_time={self.config.expiration_time}, current_size={len(self._store)})")

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SessionStore):
            return False
        with self._lock, other._lock:
            return self._store == other._store and self.config == other.config

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, SessionStore):
            return NotImplemented
        with self._lock, other._lock:
            return len(self._store) <= len(other._store)


class MODES(StrEnum):
    DEV = 'dev'
    TEST = 'test'
    PROD = 'prod'


class Environment:
    _mode: MODES = MODES.DEV

    def __init__(self, env_data: EnvPath = ".env"):
        self._env_data = self.__handle_env_path(env_data)
        self.load_env()

    @staticmethod
    def __handle_env_path(env_path: str) -> Union[PathLike, NoReturn]:
        if env_path is None:
            raise EnvError("Invalid .env data.")

        return env_path

    def load_env(self) -> None:
        dotenv.load_dotenv(dotenv_path=self._env_data)

    def read_env(self) -> Dict[str, str]:
        return dotenv.dotenv_values(self._env_data)

    def set_env(self, key: str, value: Any) -> None:
        key.upper()
        dotenv.set_key(self._env_data, key, str(value))
        self.load_env()  # Reload to update the environment

    def get_env(self, key: str) -> Optional[str]:
        return self.read_env().get(key)

    def override_env(self, key: str, value: Any) -> Dict[str, str]:

        env_vars = self.read_env()
        env_vars[key] = str(value)
        return env_vars

    def filter_env(
            self, search_value: str, search_in: Literal["key", "value"] = "key"
    ) -> List[Tuple[str, str]]:
        env_vars = self.read_env()
        if search_in == "key":
            return [(k, v) for k, v in env_vars.items() if search_value in k]
        elif search_in == "value":
            return [(k, v) for k, v in env_vars.items() if search_value in v]
        else:
            raise ValueError("search_in must be either 'key' or 'value'")

    def filter_with_predicate(
            self, predicate: Callable[[str, str], bool]
    ) -> List[Tuple[str, str]]:
        env_vars = self.read_env()
        return [(k, v) for k, v in env_vars.items() if predicate(k, v)]

    def mode(self, func_mode: MODES = MODES.TEST):
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if self._mode == func_mode:
                    return func(*args, **kwargs)
                return None

            return wrapper

        return decorator

    @classmethod
    def from_json(cls, json_path: PathLike) -> 'Environment':
        with open(json_path, 'r') as f:
            data = json.load(f)

        env = cls(env_data=json_path)

        for key, value in data.items():
            env.set_env(key, value)

        return env

    @classmethod
    def from_dict(cls, env_dict: Dict[str, Any]) -> 'Environment':
        """Create an Environment instance from a dictionary of environment variables."""
        env = cls()  # Initialize with a default env path

        for key, value in env_dict.items():
            env.set_env(key, value)

        return env

    @classmethod
    def from_config(cls, config_path: PathLike) -> 'Environment':
        config = configparser.ConfigParser()
        config.read(config_path)
        env = cls(env_data=config_path)

        # Handle both the DEFAULT section and other sections
        for section in config.sections():
            for key, value in config.items(section):
                env.set_env(key.upper(), value)

        # Also, load the DEFAULT section explicitly
        for key, value in config['DEFAULT'].items():
            env.set_env(key.upper(), value)

        return env

    def __repr__(self) -> str:
        env_vars = self.read_env()
        return (
            f"{self.__class__.__name__}(mode={self._mode}, env_path={self._env_data}, "
            f"vars={env_vars})"
        )

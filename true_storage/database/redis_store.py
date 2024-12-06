"""Redis-based storage implementation."""

import pickle
import threading
from typing import Any

import redis

from ..base import BaseStorage
from ..exceptions import StorageError, StorageConnectionError


class RedisStorage(BaseStorage):
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
                value_bytes = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                self.redis.set(self._get_key(key), value_bytes)
            except Exception as e:
                raise StorageError(f"Failed to store value: {e}")

    def retrieve(self, key: str) -> Any:
        with self._lock:
            try:
                value_bytes = self.redis.get(self._get_key(key))
                if value_bytes is None:
                    raise KeyError(f"No value found for key: {key}")
                return pickle.loads(value_bytes)
            except KeyError:
                raise
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
        new_storage = RedisStorage(
            host=self.redis.connection_pool.connection_kwargs['host'],
            port=self.redis.connection_pool.connection_kwargs['port'],
            db=self.redis.connection_pool.connection_kwargs['db'],
            prefix=f"{self.prefix}clone:"
        )
        with self._lock:
            try:
                keys = self.redis.keys(f"{self.prefix}*")
                for key in keys:
                    value_bytes = self.redis.get(key)
                    if value_bytes is not None:
                        value = pickle.loads(value_bytes)
                        new_storage.store(key[len(self.prefix):], value)
                return new_storage
            except Exception as e:
                new_storage.clear()
                raise StorageError(f"Failed to clone storage: {e}")

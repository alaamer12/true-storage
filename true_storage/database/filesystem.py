"""File system-based storage implementation."""

import pickle
import tempfile
import threading
from pathlib import Path
from typing import Optional, Any

from true_storage.base import BaseStorage
from true_storage.exceptions import StorageError


class FileSystemStorage(BaseStorage):
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
                for path in self.base_dir.glob("*.pkl"):
                    path.unlink()
            except Exception as e:
                raise StorageError(f"Failed to clear storage: {e}")

    def clone(self) -> 'FileSystemStorage':
        new_storage = FileSystemStorage(tempfile.mkdtemp())
        with self._lock:
            try:
                for path in self.base_dir.glob("*.pkl"):
                    with open(path, 'rb') as f:
                        value = pickle.load(f)
                    new_storage.store(path.stem, value)
                return new_storage
            except Exception as e:
                new_storage.clear()
                raise StorageError(f"Failed to clone storage: {e}")

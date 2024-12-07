"""File system-based database storage module.

This module provides a persistent storage implementation using the file system,
with support for atomic operations and hierarchical key storage.

Classes:
    FileSystemStorage: Main class implementing file system-based storage functionality.

Functions:
    None (all functionality is encapsulated in classes)

Types:
    None

Exceptions:
    StorageError: See :exc:`true_storage.exceptions.StorageError`
    KeyError: Raised when accessing non-existent keys

Key Features:
    - Persistent file system storage
    - Atomic write operations
    - Hierarchical key structure
    - Thread-safe operations
    - Temporary directory support
    - Key prefix filtering
    - Automatic directory management
    - Secure path validation
"""

import pickle
import tempfile
import threading
from pathlib import Path
from typing import Optional, Any, List

from true_storage.base import BaseStorage
from ..exceptions import StorageError


__all__ = [
    'FileSystemStorage',
]

def __dir__() -> List[str]:
    return sorted(__all__)

class FileSystemStorage(BaseStorage):
    """File system-based storage implementation."""

    def __init__(self, base_dir: Optional[str] = None):
        """Initialize the file system storage.
        
        Args:
            base_dir: Base directory for storage. If None, uses a temporary directory.
        """
        self.base_dir = Path(base_dir or tempfile.gettempdir()) / "checkpoints"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _get_path(self, key: str) -> Path:
        """Get a full path for a key.
        
        Args:
            key: Storage key, can include directory separators.
            
        Returns:
            Path object for the key.
        """
        # Convert key to path and ensure it's within base_dir
        path = self.base_dir / key
        if not str(path).startswith(str(self.base_dir)):
            raise StorageError("Invalid key: attempting to access outside base directory")
        return path

    def clone(self) -> 'BaseStorage':
        ...

    def store(self, key: str, value: Any) -> None:
        """Store a value with the given key.
        
        Args:
            key: Storage key
            value: Value to store
        """
        with self._lock:
            path = self._get_path(key)
            temp_path = path.with_suffix(path.suffix + '.tmp')
            
            try:
                # Create parent directories
                path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write to temporary file first
                with open(temp_path, 'wb') as f:
                    pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
                    
                # Atomic replace
                temp_path.replace(path)
            except Exception as e:
                if temp_path.exists():
                    temp_path.unlink()
                raise StorageError(f"Failed to store value: {e}")

    def retrieve(self, key: str) -> Any:
        """Retrieve a value by key.
        
        Args:
            key: Storage key
            
        Returns:
            Stored value
            
        Raises:
            KeyError: If key doesn't exist
            StorageError: If retrieval fails
        """
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
        """Delete a value by key.
        
        Args:
            key: Storage key
        """
        with self._lock:
            path = self._get_path(key)
            try:
                path.unlink(missing_ok=True)
                
                # Try to remove empty parent directories
                parent = path.parent
                while parent != self.base_dir:
                    try:
                        parent.rmdir()
                        parent = parent.parent
                    except OSError:
                        break
            except Exception as e:
                raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        """Clear all stored values."""
        with self._lock:
            try:
                # Remove all files and directories under base_dir
                for path in self.base_dir.glob("**/*"):
                    if path.is_file():
                        path.unlink()
                
                # Remove empty directories
                for path in sorted(self.base_dir.glob("**/*"), reverse=True):
                    if path.is_dir():
                        try:
                            path.rmdir()
                        except OSError:
                            pass
            except Exception as e:
                raise StorageError(f"Failed to clear storage: {e}")

    def exists(self, key: str) -> bool:
        """Check if a key exists.
        
        Args:
            key: Storage key
            
        Returns:
            True if key exists, False otherwise
        """
        path = self._get_path(key)
        return path.exists()

    def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys with given prefix.
        
        Args:
            prefix: Key prefix to filter by
            
        Returns:
            List of matching keys
        """
        prefix_path = self._get_path(prefix)
        if not prefix_path.exists():
            return []
            
        keys = []
        for path in prefix_path.parent.glob(f"{prefix_path.name}*"):
            if path.is_file():
                rel_path = path.relative_to(self.base_dir)
                keys.append(str(rel_path))
        return keys

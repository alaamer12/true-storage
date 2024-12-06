"""Cold storage implementation with compression."""

import json
import os
import zlib
import pickle
from typing import Any

from ..base import BaseStorage
from ..exceptions import StorageError


class ColdStorage(BaseStorage):
    """Cold storage implementation with compression."""

    def __init__(self, storage_directory='cold_storage', metadata_file='metadata.json'):
        self.storage_directory = storage_directory
        self.metadata_file = metadata_file
        self.metadata = {}
        self._load_metadata()
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Create the storage directory if it does not exist."""
        os.makedirs(self.storage_directory, exist_ok=True)

    def _load_metadata(self):
        """Load metadata from a JSON file."""
        metadata_path = os.path.join(self.storage_directory, self.metadata_file)
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                raise StorageError(f"Failed to load metadata: {e}")

    def _save_metadata(self):
        """Save metadata to a JSON file."""
        metadata_path = os.path.join(self.storage_directory, self.metadata_file)
        try:
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            raise StorageError(f"Failed to save metadata: {e}")

    def _compress_data(self, data: Any) -> bytes:
        """Compress data using zlib."""
        try:
            pickled_data = pickle.dumps(data)
            return zlib.compress(pickled_data)
        except Exception as e:
            raise StorageError(f"Failed to compress data: {e}")

    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data using zlib."""
        try:
            pickled_data = zlib.decompress(compressed_data)
            return pickle.loads(pickled_data)
        except Exception as e:
            raise StorageError(f"Failed to decompress data: {e}")

    def store(self, key: str, value: Any) -> None:
        try:
            compressed_data = self._compress_data(value)
            file_path = os.path.join(self.storage_directory, f"{key}.bin")
            with open(file_path, 'wb') as f:
                f.write(compressed_data)
            self.metadata[key] = {
                'size': len(compressed_data),
                'path': file_path
            }
            self._save_metadata()
        except Exception as e:
            raise StorageError(f"Failed to store value: {e}")

    def retrieve(self, key: str) -> Any:
        if key not in self.metadata:
            raise KeyError(f"No value found for key: {key}")
        try:
            file_path = self.metadata[key]['path']
            with open(file_path, 'rb') as f:
                compressed_data = f.read()
            return self._decompress_data(compressed_data)
        except Exception as e:
            raise StorageError(f"Failed to retrieve value: {e}")

    def delete(self, key: str) -> None:
        if key not in self.metadata:
            return
        try:
            file_path = self.metadata[key]['path']
            if os.path.exists(file_path):
                os.remove(file_path)
            del self.metadata[key]
            self._save_metadata()
        except Exception as e:
            raise StorageError(f"Failed to delete value: {e}")

    def clear(self) -> None:
        try:
            for key in list(self.metadata.keys()):
                self.delete(key)
            if os.path.exists(self.storage_directory):
                for file in os.listdir(self.storage_directory):
                    file_path = os.path.join(self.storage_directory, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        except Exception as e:
            raise StorageError(f"Failed to clear storage: {e}")

    def clone(self) -> 'ColdStorage':
        new_storage = ColdStorage(
            storage_directory=f"{self.storage_directory}_clone",
            metadata_file=self.metadata_file
        )
        try:
            for key in self.metadata:
                value = self.retrieve(key)
                new_storage.store(key, value)
            return new_storage
        except Exception as e:
            new_storage.clear()
            raise StorageError(f"Failed to clone storage: {e}")

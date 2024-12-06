"""Exceptions for the true_storage package."""


class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass


class StorageConnectionError(StorageError):
    """Raised when a storage connection fails."""
    pass

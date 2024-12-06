"""Base storage interface for the true_storage package."""

from abc import ABC, abstractmethod
from typing import Any


class BaseStorage(ABC):
    """Base class for all storage implementations."""

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """Store a value with the given key."""
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Any:
        """Retrieve a value by key."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a value by key."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all stored values."""
        pass

    @abstractmethod
    def clone(self) -> 'BaseStorage':
        """Create a copy of the storage instance."""
        pass

"""Storage package providing flexible data storage solutions.

This package provides a comprehensive set of storage implementations for different
use cases, from fast in-memory caching to persistent disk storage.

Classes:
    HotStorage: Fast in-memory storage with LRU caching.
    ColdStorage: Persistent disk storage with compression.
    MixedStorage: Hybrid storage combining hot and cold storage benefits.

Key Features:
    - Multiple storage implementations for different needs
    - Thread-safe operations across all storage types
    - Configurable policies and optimization strategies
    - Performance monitoring and metrics
    - Event-driven architecture
    - Automatic resource management
"""

from typing import List
from .base import StoragePolicy
from .cold import ColdStorage
from .hot import HotStorage
from .mixed import MixedStorage

__all__ = [
    'HotStorage',
    'ColdStorage',
    'MixedStorage',
    'StoragePolicy'
]

def __dir__() -> List[str]:
    return sorted(__all__)

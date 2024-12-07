"""
True Storage: Advanced Environment and Storage Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

True Storage is a subpackage of True Core (https://github.com/alaamer12/true-core), providing
comprehensive environment and storage management solutions for Python applications.

Classes:
    Environment: Manages application environments with mode-based configuration.
    SessionStore: Handles user sessions with persistence and monitoring.
    StoragePolicy: Defines storage behavior and error handling policies.
    
    Storage Implementations:
        HotStorage: Fast in-memory storage with LRU caching.
        ColdStorage: Persistent disk storage with compression.
        MixedStorage: Hybrid storage combining hot and cold storage benefits.
    
    Database Storage:
        FileSystemStorage: Local file system-based storage.
        SQLiteStorage: SQLite database storage.
        RedisStorage: Redis-based storage (under development).

Types:
    SessionStatus: Enum for session states (ACTIVE, LOCKED, EXPIRED).
    SessionMetadata: Data class for session tracking information.
    StoragePolicy: Enum for storage behavior (STRICT, RELAXED).

Exceptions:
    StorageError: Base exception for storage-related errors.
    ModeError: Raised when accessing variables in incorrect mode.
    ConfigError: Configuration-related errors.

Key Features:
    - Mode-based Configuration: Switch between dev, test, staging, and production.
    - Dynamic Environment Handling: Runtime environment variable management.
    - Type Safety: Automatic type checking and conversion.
    - Secure Secret Management: Built-in security for sensitive data.
    - Flexible Storage: Multiple backend options with optimization.
    - Session Management: Efficient user session handling.
    - Database Integration: Multiple database storage options.
    - Event-driven Architecture: Rich event system for monitoring.
    - Performance Monitoring: Built-in metrics and optimization.
    - Thread Safety: Concurrent operation support.
"""

__title__ = "true-storage"
__version__ = "0.1.0"
__author__ = "alaamer12"
__author_email__ = "ahmedmuhmmed239@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2024 alaamer12"
__description__ = "A boilerplate utility package"
__url__ = "https://github.com/alaamer12/true-storage"
__keywords__ = [
]

__all__ = [
    "__title__",
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "__description__",
    "__url__",
    "__keywords__",
    "get_version",
    "get_author",
    "get_description",
]


def get_version() -> str:
    """Return the version of true."""
    return __version__


def get_author() -> str:
    """Return the author of true."""
    return __author__


def get_description() -> str:
    """Return the description of true."""
    return __description__


def __dir__():
    """Return a sorted list of names in this module."""
    return sorted(__all__)

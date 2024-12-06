"""Base classes and utilities for storage implementations."""

import abc
import enum
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic

T = TypeVar('T')


class StoragePolicy(enum.Enum):
    """Storage policies for data management."""
    STRICT = 'strict'  # Throw error on issues
    LENIENT = 'lenient'  # Try to recover from issues
    LAZY = 'lazy'  # Defer operations when possible


@dataclass
class StorageMetrics:
    """Storage metrics for monitoring."""
    hits: int = 0
    misses: int = 0
    total_operations: int = 0
    total_errors: int = 0
    avg_response_time: float = 0.0
    storage_size: int = 0
    last_cleanup_time: float = 0.0


class StorageEvent:
    """Base class for storage events."""

    def __init__(self, storage_id: str, event_type: str, data: Any = None):
        self.storage_id = storage_id
        self.event_type = event_type
        self.data = data
        self.timestamp = time.time()


class StorageEventHandler(abc.ABC):
    """Abstract base class for storage event handlers."""

    @abc.abstractmethod
    def handle_event(self, event: StorageEvent) -> None:
        """Handle a storage event."""
        pass


class StorageOptimizer(abc.ABC):
    """Abstract base class for storage optimizers."""

    @abc.abstractmethod
    def optimize(self, data: Any) -> Any:
        """Optimize data for storage."""
        pass

    @abc.abstractmethod
    def deoptimize(self, data: Any) -> Any:
        """Restore data from optimized form."""
        pass


class StorageStrategy(abc.ABC, Generic[T]):
    """Abstract base class for storage strategies."""

    @abc.abstractmethod
    def store(self, key: str, value: T) -> None:
        """Store a value."""
        pass

    @abc.abstractmethod
    def retrieve(self, key: str) -> Optional[T]:
        """Retrieve a value."""
        pass

    @abc.abstractmethod
    def delete(self, key: str) -> None:
        """Delete a value."""
        pass


class BaseStorageManager:
    """Base class for storage management."""

    def __init__(
            self,
            storage_id: str,
            policy: StoragePolicy = StoragePolicy.STRICT,
            event_handlers: Optional[List[StorageEventHandler]] = None,
            optimizer: Optional[StorageOptimizer] = None
    ):
        self.storage_id = storage_id
        self.policy = policy
        self.event_handlers = event_handlers or []
        self.optimizer = optimizer
        self.metrics = StorageMetrics()
        self._callbacks: Dict[str, List[Callable]] = {}

    def add_event_handler(self, handler: StorageEventHandler) -> None:
        """Add an event handler."""
        self.event_handlers.append(handler)

    def emit_event(self, event_type: str, data: Any = None) -> None:
        """Emit a storage event."""
        event = StorageEvent(self.storage_id, event_type, data)
        for handler in self.event_handlers:
            try:
                handler.handle_event(event)
            except Exception:
                if self.policy == StoragePolicy.STRICT:
                    raise

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type."""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)

    def _trigger_callbacks(self, event_type: str, *args, **kwargs) -> None:
        """Trigger callbacks for an event type."""
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                if self.policy == StoragePolicy.STRICT:
                    raise

    def update_metrics(self, operation: str, success: bool, response_time: float) -> None:
        """Update storage metrics."""
        self.metrics.total_operations += 1
        if operation == 'retrieve':
            if success:
                self.metrics.hits += 1
            else:
                self.metrics.misses += 1
        if not success:
            self.metrics.total_errors += 1
        # Update average response time using moving average
        self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * (self.metrics.total_operations - 1) + response_time)
                / self.metrics.total_operations
        )

    def get_metrics(self) -> StorageMetrics:
        """Get current storage metrics."""
        return self.metrics

    def optimize_data(self, data: Any) -> Any:
        """Optimize data for storage."""
        if self.optimizer:
            return self.optimizer.optimize(data)
        return data

    def deoptimize_data(self, data: Any) -> Any:
        """Restore data from optimized form."""
        if self.optimizer:
            return self.optimizer.deoptimize(data)
        return data

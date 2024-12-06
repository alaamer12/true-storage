Storage Examples
================

This section demonstrates True Storage's core storage capabilities, including hot (in-memory), cold (disk-based), and mixed (tiered) storage strategies.

Storage Types Overview
----------------------

True Storage provides three main storage types:

1. **Hot Storage**: In-memory storage with LRU caching
2. **Cold Storage**: Disk-based storage with compression
3. **Mixed Storage**: Tiered storage combining hot and cold strategies

Hot Storage
-----------

Hot storage provides fast, in-memory data access with LRU (Least Recently Used) caching:

.. literalinclude:: ../../../../true_storage/demos/storage/01_hot_storage.py
   :language: python
   :caption: Hot Storage Operations
   :linenos:
   :emphasize-lines: 15-16,25-26,35-36
   :name: hot-storage-example

Key features demonstrated:
 - In-memory caching with configurable size
 - LRU eviction for memory management
 - Thread-safe operations
 - Performance metrics and statistics
 - Optional item expiration

Usage Tips:
 - Ideal for frequently accessed data
 - Monitor memory usage with ``get_stats()``
 - Set appropriate ``max_size`` for your use case
 - Use ``set_ttl()`` for time-sensitive data

Cold Storage
------------

Cold storage provides persistent, disk-based storage with compression:

.. literalinclude:: ../../../../true_storage/demos/storage/02_cold_storage.py
   :language: python
   :caption: Cold Storage Operations
   :linenos:
   :emphasize-lines: 18-19,28-29,38-39
   :name: cold-storage-example

Key features demonstrated:
 - File-based persistent storage
 - Automatic data compression
 - Metadata tracking and statistics
 - Atomic file operations
 - Directory management

Best Practices:
 - Use for large, infrequently accessed data
 - Enable compression for large datasets
 - Monitor disk usage with ``get_stats()``
 - Implement proper error handling
 - Use context managers for safe operations

Mixed Storage
-------------

Mixed storage combines hot and cold storage for optimal performance:

.. literalinclude:: ../../../../true_storage/demos/storage/03_mixed_storage.py
   :language: python
   :caption: Mixed Storage Operations
   :linenos:
   :emphasize-lines: 20-21,35-36,50-51
   :name: mixed-storage-example

Key features demonstrated:
 - Automatic tiered storage management
 - Smart data migration based on access patterns
 - Combined statistics and monitoring
 - Optimized read/write operations
 - Configurable storage ratios

Performance Tips:
 - Tune hot/cold ratio based on workload
 - Monitor access patterns with ``get_stats()``
 - Use appropriate storage backends
 - Implement proper error handling
 - Consider data locality

Advanced Usage
--------------

Here are some advanced storage patterns:

.. code-block:: python

    from true_storage.storage import MixedStorage
    from true_storage.compression import ZstdCompression
    
    # Create a mixed storage with custom configuration
    storage = MixedStorage(
        hot_size=1000,            # Hot storage size
        cold_path="/data/cache",  # Cold storage path
        compression=ZstdCompression(level=3),  # Custom compression
        hot_ratio=0.2,           # Keep 20% in hot storage
        stats_enabled=True       # Enable detailed statistics
    )
    
    # Store with metadata
    storage.store(
        "key1",
        "value1",
        metadata={
            "type": "user_data",
            "priority": "high",
            "ttl": 3600  # 1 hour
        }
    )
    
    # Bulk operations
    with storage.batch() as batch:
        batch.store("key2", "value2")
        batch.store("key3", "value3")
    
    # Get storage statistics
    stats = storage.get_stats()
    print(f"Hot storage hit ratio: {stats.hot_hit_ratio}%")
    print(f"Cold storage size: {stats.cold_size_bytes} bytes")

Error Handling
--------------

Proper error handling is crucial for robust storage operations:

.. code-block:: python

    from true_storage.exceptions import StorageError, StorageFullError
    
    try:
        storage.store("key", "value")
    except StorageFullError:
        # Handle storage capacity issues
        storage.evict_least_used(count=10)
        storage.store("key", "value")
    except StorageError as e:
        # Handle other storage errors
        logger.error(f"Storage error: {e}")
        raise

See Also
--------

- :doc:`../database/index` - Database storage examples
- :doc:`../../api_reference` - API reference documentation
- :doc:`../../modules/index` - Module documentation

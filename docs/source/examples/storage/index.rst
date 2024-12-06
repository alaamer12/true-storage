Storage Examples
===============

This section contains examples demonstrating the core storage capabilities of True Storage.

Hot Storage
---------

The following example demonstrates in-memory hot storage operations:

.. literalinclude:: ../../../../true_storage/demos/storage/01_hot_storage.py
   :language: python
   :caption: Hot Storage Operations
   :linenos:
   :name: hot-storage-example

Key features demonstrated:
 - In-memory caching
 - LRU eviction
 - Performance metrics
 - Thread safety

Cold Storage
----------

This example shows disk-based cold storage operations:

.. literalinclude:: ../../../../true_storage/demos/storage/02_cold_storage.py
   :language: python
   :caption: Cold Storage Operations
   :linenos:
   :name: cold-storage-example

Key features demonstrated:
 - File-based storage
 - Data compression
 - Metadata tracking
 - Atomic operations

Mixed Storage
-----------

The following example demonstrates tiered storage using both hot and cold storage:

.. literalinclude:: ../../../../true_storage/demos/storage/03_mixed_storage.py
   :language: python
   :caption: Mixed Storage Operations
   :linenos:
   :name: mixed-storage-example

Key features demonstrated:
 - Tiered storage strategy
 - Automatic data migration
 - Access pattern optimization
 - Performance monitoring

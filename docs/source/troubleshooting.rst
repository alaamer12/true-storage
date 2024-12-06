Troubleshooting Guide
=====================

This guide helps you resolve common issues when using True Storage.

Installation Issues
-------------------

ModuleNotFoundError: No module named 'true_storage'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: The package is not properly installed or not in Python's path.

**Solutions**:

1. Verify installation:

   .. code-block:: bash

       pip show true-storage

2. Reinstall the package:

   .. code-block:: bash

       pip install --force-reinstall true-storage

3. Check Python environment:

   .. code-block:: bash

       python -c "import sys; print(sys.path)"

ImportError: No module named 'pydantic_settings'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Missing Pydantic settings package required for environment features.

**Solutions**:

1. For Pydantic v1:

   .. code-block:: bash

       pip install "pydantic-settings<2.0"

2. For Pydantic v2:

   .. code-block:: bash

       pip install "pydantic-settings>=2.0"

Storage Issues
--------------

StorageFullError: Storage capacity exceeded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Hot storage has reached its maximum capacity.

**Solutions**:

1. Increase storage size:

   .. code-block:: python

       storage = HotStorage(max_size=2000)  # Increase from default

2. Enable automatic eviction:

   .. code-block:: python

       storage = HotStorage(auto_evict=True)

3. Manually evict items:

   .. code-block:: python

       storage.evict_least_used(count=10)

FileNotFoundError: Storage path does not exist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Cold storage directory doesn't exist or isn't accessible.

**Solutions**:

1. Create directory manually:

   .. code-block:: python

       import os
       os.makedirs("/path/to/storage", exist_ok=True)

2. Use absolute paths:

   .. code-block:: python

       import os
       storage = ColdStorage(path=os.path.abspath("./storage"))

3. Check permissions:

   .. code-block:: bash

       # Windows
       icacls "C:\path\to\storage"
       
       # Unix
       ls -la /path/to/storage

Session Issues
--------------

SessionExpiredError: Session has expired
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Session timeout occurred before access.

**Solutions**:

1. Increase session timeout:

   .. code-block:: python

       session = Session(timeout=3600)  # 1 hour

2. Enable auto-refresh:

   .. code-block:: python

       session = Session(auto_refresh=True)

3. Manually refresh session:

   .. code-block:: python

       session.refresh()

ConcurrencyError: Session locked
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Multiple threads attempting to access session simultaneously.

**Solutions**:

1. Use context manager:

   .. code-block:: python

       with session.lock():
           session.set("key", "value")

2. Enable thread-safe mode:

   .. code-block:: python

       session = Session(thread_safe=True)

3. Implement retry logic:

   .. code-block:: python

       from time import sleep
       
       def retry_session_op(session, max_retries=3):
           for i in range(max_retries):
               try:
                   with session.lock():
                       return session.get("key")
               except ConcurrencyError:
                   if i == max_retries - 1:
                       raise
                   sleep(0.1 * (i + 1))

Environment Issues
------------------

ValidationError: Invalid environment variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Environment variable doesn't match expected type or format.

**Solutions**:

1. Use type conversion:

   .. code-block:: python

       env = Environment(
           type_hints={"PORT": int, "DEBUG": bool}
       )

2. Provide default values:

   .. code-block:: python

       env = Environment(
           defaults={"PORT": 8000, "DEBUG": False}
       )

3. Add custom validation:

   .. code-block:: python

       def validate_port(value):
           port = int(value)
           if not 1 <= port <= 65535:
               raise ValueError("Invalid port number")
           return port

       env = Environment(
           validators={"PORT": validate_port}
       )

ModeError: Invalid environment mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Attempting to use undefined environment mode.

**Solutions**:

1. Use predefined modes:

   .. code-block:: python

       from true_storage.env import MODES
       
       env = Environment(mode=MODES.DEVELOPMENT)

2. Register custom mode:

   .. code-block:: python

       env = Environment()
       env.register_mode("STAGING", parent=MODES.DEVELOPMENT)

3. Check current mode:

   .. code-block:: python

       print(f"Current mode: {env.current_mode}")

Performance Issues
------------------

Slow Storage Operations
~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Storage operations taking longer than expected.

**Solutions**:

1. Use appropriate storage type:

   .. code-block:: python

       # For frequent access
       hot_storage = HotStorage()
       
       # For large data
       cold_storage = ColdStorage(compression=True)
       
       # For balanced performance
       mixed_storage = MixedStorage(hot_ratio=0.3)

2. Enable caching:

   .. code-block:: python

       storage = ColdStorage(cache_size=1000)

3. Monitor performance:

   .. code-block:: python

       stats = storage.get_stats()
       print(f"Hit ratio: {stats.hit_ratio}%")
       print(f"Average access time: {stats.avg_access_time}ms")

Memory Usage Issues
~~~~~~~~~~~~~~~~~~~

**Problem**: High memory consumption.

**Solutions**:

1. Configure storage limits:

   .. code-block:: python

       storage = HotStorage(
           max_size=1000,
           max_memory_mb=100
       )

2. Enable compression:

   .. code-block:: python

       from true_storage.compression import ZstdCompression
       
       storage = ColdStorage(
           compression=ZstdCompression(level=3)
       )

3. Implement cleanup:

   .. code-block:: python

       # Periodic cleanup
       storage.cleanup(
           max_age=3600,  # 1 hour
           min_free_space=1024 * 1024 * 100  # 100MB
       )

Getting Help
------------

If you continue to experience issues:

1. Check the :doc:`examples/index` for proper usage patterns
2. Review the :doc:`modules/index` for detailed API documentation
3. Visit our `GitHub Issues <https://github.com/yourusername/true-storage/issues>`_
4. Join our `Discord Community <https://discord.gg/true-storage>`_
5. Contact support at support@true-storage.dev

See Also
--------

- :doc:`installation` - Installation guide
- :doc:`examples/index` - Usage examples
- :doc:`modules/index` - API reference
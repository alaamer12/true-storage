Environment Module
==================

.. admonition:: Core Feature
   :class: important

   The Environment module is the heart of True Storage, providing powerful environment management 
   with mode support, runtime configuration, and advanced stage management capabilities.

Overview
--------

.. module:: true_storage.env
   :no-index:

The Environment module offers a robust solution for managing configuration across different
environments (development, testing, production) with features like:

* **Mode-Based Configuration**: Switch between different environments seamlessly
* **Runtime Configuration**: Change settings dynamically during execution
* **Stage Management**: Define and manage custom stages beyond traditional environments
* **Decorator Support**: Control function execution based on environment modes
* **State Management**: Create and restore configuration snapshots
* **Type Safety**: Validate configuration values with type checking

Key Components
--------------

Environment Class
~~~~~~~~~~~~~~~~~

.. autoclass:: true_storage.env.Environment
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Modes
~~~~~

.. autoclass:: true_storage.env.MODES
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Usage Examples
--------------

Basic Usage
~~~~~~~~~~~

.. code-block:: python
   :emphasize-lines: 2,5
   
   # Initialize environment with mode
   env = Environment(mode=MODES.DEV)
   
   # Set environment variables
   env.set("DATABASE_URL", "postgresql://localhost:5432/db", modes=[MODES.DEV])
   env.set("DATABASE_URL", "postgresql://prod:5432/db", modes=[MODES.PROD])
   
   # Get current environment variable
   db_url = env.get("DATABASE_URL")  # Returns dev URL in DEV mode

Mode Switching
~~~~~~~~~~~~~~

.. code-block:: python
   :emphasize-lines: 2,6,10
   
   # Using context manager
   with env.with_mode(MODES.PROD):
       prod_url = env.get("DATABASE_URL")  # Gets production URL
   
   # Using mode property
   env.mode = MODES.TEST
   test_config = env.get("TEST_CONFIG")
   
   # Using decorators
   @env.mark(MODES.PROD)
   def production_task():
       # Only runs in production mode
       pass

Advanced Features
~~~~~~~~~~~~~~~~~

.. code-block:: python
   :emphasize-lines: 2,7,12
   
   # Create configuration snapshot
   snapshot = env.create_snapshot()
   
   # Make temporary changes
   env.set("TEMP_VAR", "temporary")
   
   # Restore previous state
   env.rollback(snapshot)
   
   # Custom stages
   env.with_stage(STAGING="staging", QA="qa")
   @env.mark(MODES.STAGING)
   def staging_task():
       pass

Best Practices
--------------

1. **Mode Management**:
   - Always set a default mode during initialization
   - Use context managers for temporary mode switches
   - Avoid global mode changes in library code

2. **Variable Handling**:
   - Use type hints for better validation
   - Set defaults for optional variables
   - Group related variables by mode

3. **State Management**:
   - Create snapshots before major changes
   - Use rollback for testing and cleanup
   - Maintain separate configurations per mode

4. **Security**:
   - Never store sensitive data in code
   - Use separate files for different environments
   - Implement proper access controls

See Also
--------

- :doc:`../api_reference` - Complete API documentation
- :doc:`storage` - Storage backend integration
- :doc:`session` - Session management
- :doc:`database` - Database configuration

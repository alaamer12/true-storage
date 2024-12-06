Installation Guide
==================

This guide covers installing True Storage and its dependencies.

Requirements
------------

- Python 3.8 or higher
- pip package manager
- Optional: virtualenv or conda for isolated environments

Basic Installation
------------------

Install True Storage using pip:

.. code-block:: bash

    pip install true-storage

For development installation with extra tools:

.. code-block:: bash

    pip install true-storage[dev]

Installation Options
--------------------

True Storage provides several installation options for different use cases:

Core Installation
~~~~~~~~~~~~~~~~~

Basic installation with core features:

.. code-block:: bash

    pip install true-storage

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

Installation with development tools:

.. code-block:: bash

    pip install true-storage[dev]

Includes:
 - pytest for testing
 - black for code formatting
 - mypy for type checking
 - sphinx for documentation

Full Installation
~~~~~~~~~~~~~~~~~

All features and optional dependencies:

.. code-block:: bash

    pip install true-storage[full]

Includes:
 - All compression backends
 - All storage backends
 - Performance monitoring
 - Advanced features

Minimal Installation
~~~~~~~~~~~~~~~~~~~~

Minimal installation with basic features:

.. code-block:: bash

    pip install true-storage[minimal]

Database Backends
-----------------

Install specific database backends:

SQLite (included by default):
    No additional installation required

Redis:
    .. code-block:: bash

        pip install true-storage[redis]

MongoDB:
    .. code-block:: bash

        pip install true-storage[mongodb]

Compression Options
-------------------

Install compression backends:

zlib (included by default):
    No additional installation required

zstd:
    .. code-block:: bash

        pip install true-storage[zstd]

lz4:
    .. code-block:: bash

        pip install true-storage[lz4]

Pydantic Integration
--------------------

True Storage provides full compatibility with Pydantic for data validation and serialization.

Basic Integration
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pydantic import BaseModel
    from true_storage.storage import HotStorage
    from true_storage.serializers import PydanticSerializer

    class User(BaseModel):
        id: int
        name: str
        email: str

    # Create storage with Pydantic serializer
    storage = HotStorage(serializer=PydanticSerializer())

    # Store Pydantic model
    user = User(id=1, name="Alice", email="alice@example.com")
    storage.store("user:1", user)

    # Retrieve as Pydantic model
    retrieved_user = storage.retrieve("user:1")
    print(retrieved_user.name)  # Output: Alice

Version Compatibility
~~~~~~~~~~~~~~~~~~~~~

Pydantic v1:
    .. code-block:: bash

        pip install true-storage[pydantic-v1]

Pydantic v2:
    .. code-block:: bash

        pip install true-storage[pydantic-v2]

Advanced Features:
 - Schema validation
 - Type coercion
 - Custom serializers
 - Model inheritance

Development Setup
-----------------

For development, we recommend using a virtual environment:

.. code-block:: bash

    # Create virtual environment
    python -m venv venv
    
    # Activate virtual environment
    # Windows
    venv\Scripts\activate
    # Unix/macOS
    source venv/bin/activate
    
    # Install development dependencies
    pip install -e ".[dev]"

Testing Installation
--------------------

Verify your installation:

.. code-block:: python

    import true_storage
    
    # Print version
    print(true_storage.__version__)
    
    # Test basic functionality
    from true_storage.storage import HotStorage
    
    storage = HotStorage()
    storage.store("test", "value")
    assert storage.retrieve("test") == "value"
    print("Installation test successful!")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. **ImportError: No module named 'true_storage'**
   
   Solution: Verify installation:
   
   .. code-block:: bash

       pip show true-storage
       pip install --force-reinstall true-storage

2. **Dependency Conflicts**
   
   Solution: Use virtual environment:
   
   .. code-block:: bash

       python -m venv fresh_env
       fresh_env\Scripts\activate  # Windows
       pip install true-storage

3. **Compilation Issues**
   
   Solution: Install build tools:
   
   .. code-block:: bash

       # Windows
       pip install --upgrade setuptools wheel
       
       # Unix/macOS
       sudo apt-get install python3-dev build-essential  # Ubuntu
       brew install python-dev  # macOS

Getting Help
------------

If you encounter issues:

1. Check our `GitHub Issues <https://github.com/yourusername/true-storage/issues>`_
2. Join our `Discord Community <https://discord.gg/true-storage>`_
3. Read the :doc:`troubleshooting` guide
4. Contact support at support@true-storage.dev

See Also
--------


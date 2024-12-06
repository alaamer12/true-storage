Examples
========

This section provides comprehensive examples demonstrating various features of True Storage.

.. toctree::
   :maxdepth: 2
   :caption: Example Categories:

   examples/index

Quick Start
-----------

Here's a quick example to get you started:

.. code-block:: python

    from true_storage.storage import HotStorage
    
    # Create a hot storage instance
    storage = HotStorage(max_size=1000)
    
    # Store some data
    storage.store("key1", "Hello World!")
    
    # Retrieve data
    value = storage.retrieve("key1")
    print(value)  # Output: Hello World!

For more detailed examples, check out the specific categories above:

- **Database Examples**: Working with SQLite and filesystem storage
- **Environment Examples**: Managing configuration and environment variables
- **Session Examples**: Handling user sessions and state
- **Storage Examples**: Using hot, cold, and mixed storage strategies

Examples and Tutorials
======================

.. code-block:: text
   :class: banner

   ╔════════════════════════════════════════════════════════════╗
   ║                  True Storage Examples                     ║
   ║           Learn, Build, and Master True Storage            ║
   ╚════════════════════════════════════════════════════════════╝

Welcome to True Storage's examples and tutorials section! Here you'll find comprehensive guides and practical examples to help you make the most of True Storage's features.

Quick Start Examples
--------------------

.. grid:: 2

    .. grid-item-card:: 🔥 Storage Examples
        :link: storage/index
        :link-type: doc

        Learn how to use different storage backends for various use cases.
        Perfect for getting started with True Storage's core functionality.

    .. grid-item-card:: 🔄 Session Examples
        :link: session/index
        :link-type: doc

        Explore session management capabilities with practical examples
        showing how to handle user sessions effectively.

Advanced Usage
--------------

.. grid:: 2

    .. grid-item-card:: 🌍 Environment Examples
        :link: env/index
        :link-type: doc

        Master environment variable management and configuration
        with real-world scenarios and best practices.

    .. grid-item-card:: 📚 Database Examples
        :link: database/index
        :link-type: doc

        Learn how to work with different database storage options
        and integrate with various persistence layers.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Basic Examples:

   storage/index
   session/index
   env/index
   database/index

Code Snippets
-------------

Basic Storage Operations
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :caption: Simple key-value storage
    :emphasize-lines: 6,7

    from true_storage import HotStorage

    # Initialize storage
    storage = HotStorage()

    # Store and retrieve data
    storage.set("user_id", 12345)
    value = storage.get("user_id")  # Returns: 12345

Session Management
~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :caption: Basic session handling
    :emphasize-lines: 5,8

    from true_storage import Session

    # Create a new session
    session = Session()
    session.start()

    # Use the session
    with session.active():
        session.set("cart", ["item1", "item2"])

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :caption: Environment configuration
    :emphasize-lines: 7,8

    from true_storage import Environment
    from true_storage.env import MODES

    # Initialize environment
    env = Environment()

    # Access environment variables
    env.set("DEBUG", True, mode=MODES.DEVELOPMENT)
    debug_mode = env.get("DEBUG")  # Returns: True

Best Practices
--------------

- Always use context managers for session operations
- Implement proper error handling
- Choose appropriate storage backend for your use case
- Configure compression for large datasets
- Monitor performance metrics
- Follow security guidelines

Next Steps
----------

- Explore the :doc:`../modules/index` for detailed API documentation
- Check out the :doc:`../troubleshooting` guide for common issues
- Join our community for support and discussions

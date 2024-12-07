API Reference
=============


.. raw:: html

   <div class="banner-container">
      <img src="_static/light_true_banner.png" class="banner light-banner" alt="True Storage Banner">
      <img src="_static/dark_true_banner.png" class="banner dark-banner" alt="True Storage Banner">
   </div>

This section provides detailed API documentation for True Storage's core modules and components.

Core Components
---------------

.. grid:: 2

    .. grid-item-card:: Storage
        :link: modules/storage
        :link-type: doc

        Storage backends including Hot, Cold, and Mixed storage implementations.

    .. grid-item-card:: Session
        :link: modules/session
        :link-type: doc

        Session management and persistence functionality.

    .. grid-item-card:: Environment
        :link: modules/env
        :link-type: doc

        Environment variable handling and configuration management.

    .. grid-item-card:: Database
        :link: modules/database
        :link-type: doc

        Database integration and persistence layer.

Module Reference
----------------

Storage Module
~~~~~~~~~~~~~~

.. automodule:: true_storage.storage
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Session Module
~~~~~~~~~~~~~~

.. automodule:: true_storage.session
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Environment Module
~~~~~~~~~~~~~~~~~~

.. automodule:: true_storage.env
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Database Module
~~~~~~~~~~~~~~~

.. automodule:: true_storage.database
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. note::
   For storage-related errors, see :exc:`~true_storage.exceptions.StorageError` in the Exceptions section.

Utility Functions
-----------------

Exceptions
----------

.. automodule:: true_storage.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. note::
   The :exc:`true_storage.exceptions.StorageError` is the base exception class for all storage-related errors.
   It is imported and used by both filesystem and SQLite storage modules.

See Also
--------

- :doc:`modules/index` - Detailed module documentation
- :doc:`examples/index` - Usage examples
- :doc:`troubleshooting` - Troubleshooting guide

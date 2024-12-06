Database Examples
=================

This section contains examples demonstrating the database storage capabilities of True Storage.

Basic SQLite Storage
--------------------

The following example demonstrates basic operations with SQLite storage:

.. literalinclude:: ../../../../true_storage/demos/database/01_basic_sqlite.py
   :language: python
   :caption: Basic SQLite Storage Example
   :linenos:
   :emphasize-lines: 35-36,42-43
   :name: basic-sqlite-example

Key features demonstrated:
 - SQLite storage initialization
 - Storing and retrieving data
 - Deleting data
 - Error handling

Filesystem Storage
------------------

The following example shows how to use filesystem-based storage:

.. literalinclude:: ../../../../true_storage/demos/database/02_filesystem_store.py
   :language: python
   :caption: Filesystem Storage Example
   :linenos:
   :emphasize-lines: 41-42,46-47
   :name: filesystem-storage-example

Key features demonstrated:
 - Filesystem storage initialization
 - Hierarchical storage with directories
 - Atomic file operations
 - Directory cleanup

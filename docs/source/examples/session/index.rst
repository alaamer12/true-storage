Session Examples
===============

This section contains examples demonstrating the session management capabilities of True Storage.

Basic Session Usage
----------------

The following example shows basic session operations:

.. literalinclude:: ../../../../true_storage/demos/session/01_basic_session.py
   :language: python
   :caption: Basic Session Usage
   :linenos:
   :name: basic-session-example

Key features demonstrated:
 - Session creation
 - Data storage and retrieval
 - Session cleanup
 - Basic error handling

Session Expiration
---------------

This example demonstrates session expiration handling:

.. literalinclude:: ../../../../true_storage/demos/session/02_expiration.py
   :language: python
   :caption: Session Expiration Handling
   :linenos:
   :name: session-expiration-example

Key features demonstrated:
 - Setting session timeouts
 - Handling expired sessions
 - Auto-cleanup
 - Time-based operations

Session Locking
------------

The following example shows thread-safe session operations:

.. literalinclude:: ../../../../true_storage/demos/session/03_locking.py
   :language: python
   :caption: Thread-Safe Session Operations
   :linenos:
   :name: session-locking-example

Key features demonstrated:
 - Thread synchronization
 - Lock acquisition
 - Deadlock prevention
 - Concurrent access

Session Persistence
---------------

This example demonstrates session persistence features:

.. literalinclude:: ../../../../true_storage/demos/session/04_persistence.py
   :language: python
   :caption: Session Persistence
   :linenos:
   :name: session-persistence-example

Key features demonstrated:
 - Session storage backends
 - Data persistence
 - Recovery mechanisms
 - Backend configuration

Advanced Session Features
---------------------

This example shows advanced session management features:

.. literalinclude:: ../../../../true_storage/demos/session/05_advanced.py
   :language: python
   :caption: Advanced Session Features
   :linenos:
   :name: advanced-session-example

Key features demonstrated:
 - Custom session handlers
 - Event callbacks
 - Session migration
 - Advanced configuration

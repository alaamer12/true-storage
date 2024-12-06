Environment Examples
====================

This section contains examples demonstrating the environment management capabilities of True Storage.

Basic Environment Usage
-----------------------

The following example shows basic environment variable handling:

.. literalinclude:: ../../../../true_storage/demos/env/01_basic_env.py
   :language: python
   :caption: Basic Environment Usage
   :linenos:
   :name: basic-env-example

Key features demonstrated:
 - Loading environment variables
 - Accessing environment values
 - Environment variable validation
 - Default values

Mode-Specific Configuration
---------------------------

This example demonstrates mode-specific environment configurations:

.. literalinclude:: ../../../../true_storage/demos/env/02_mode_specific.py
   :language: python
   :caption: Mode-Specific Environment Configuration
   :linenos:
   :name: mode-specific-env-example

Key features demonstrated:
 - Development vs Production modes
 - Mode-specific variables
 - Environment inheritance
 - Configuration overrides

Environment Snapshots
---------------------

The following example shows how to work with environment snapshots:

.. literalinclude:: ../../../../true_storage/demos/env/03_snapshots.py
   :language: python
   :caption: Environment Snapshots
   :linenos:
   :name: env-snapshots-example

Key features demonstrated:
 - Creating environment snapshots
 - Restoring from snapshots
 - Snapshot comparison
 - State management

Advanced Environment Features
-----------------------------

This example demonstrates advanced environment management features:

.. literalinclude:: ../../../../true_storage/demos/env/04_advanced.py
   :language: python
   :caption: Advanced Environment Features
   :linenos:
   :name: advanced-env-example

Key features demonstrated:
 - Environment validation
 - Custom type conversion
 - Environment inheritance
 - Dynamic configuration

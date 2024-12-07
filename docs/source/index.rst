True Storage Documentation
==========================

.. raw:: html

   <div class="banner-container">
      <img src="_static/light_true_banner.png" class="banner light-banner" alt="True Storage Banner">
      <img src="_static/dark_true_banner.png" class="banner dark-banner" alt="True Storage Banner">
   </div>

.. image:: https://img.shields.io/badge/python-3.8%2B-blue
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :alt: MIT License
   :target: https://choosealicense.com/licenses/mit/

.. image:: https://img.shields.io/badge/pydantic-v1%20%7C%20v2-blue
   :alt: Pydantic Support

.. grid:: 2

    .. grid-item::
        :columns: 12

        .. card:: Environment Module
            :link: modules/env.html
            :class-card: highlight-card

            The core of True Storage, providing powerful environment management with:

            * Mode-based configuration
            * Runtime configuration switching
            * Advanced stage management
            * Type-safe variable handling
            * External environment integration

    .. grid-item::
        :columns: 12

        .. card:: Storage Backend
            :link: modules/storage.html

            Flexible storage solutions for your data:

            * File system storage
            * Memory storage
            * Custom backend support

.. grid:: 3

    .. grid-item::
        :columns: 12

        .. card:: Session Management
            :link: modules/session.html

            Manage application sessions with ease.

    .. grid-item::
        :columns: 12

        .. card:: Database Integration
            :link: modules/database.html

            Seamless database configuration and management.

True Storage is an advanced environment management system for Python applications, offering powerful features for configuration, validation, and secure environment handling.

Key Features
------------

True Storage offers a comprehensive set of features designed to simplify and enhance environment management in Python applications:

* 🔀 **Mode-based Configuration**: Easily switch between development, testing, staging, and production environments.
* 🔄 **Dynamic Environment Handling**: Update and access environment variables at runtime.
* 🛡️ **Type Safety**: Automatic type checking and conversion for environment variables.
* 🔒 **Secure Secret Management**: Built-in support for handling sensitive information securely.
* 💾 **Flexible Storage Backend**: Choose from file system, memory, or custom storage solutions.
* 👤 **Session Management**: Efficiently manage user sessions across your application.
* 🗄️ **Database Integration**: Seamlessly configure and manage database connections.
* 📊 **Pydantic Integration**: Leverage Pydantic for robust data validation and settings management.
* 🌍 **External Environment Support**: Seamlessly integrate with system environment variables.

Getting Started
---------------

.. toctree::
   :maxdepth: 2
   :caption: Quick Start Guide

   installation
   examples
   examples/index
   troubleshooting

API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Developer Reference

   api_reference
   modules/index

Project Info
------------

.. toctree::
   :maxdepth: 1
   :caption: Development

   releases


Code Example
------------

.. code-block:: python
   :emphasize-lines: 1,4,7,13,18,23,28
   :caption: Environment Module Example

   from true_storage.env import Environment, MODES
   
   # Create environment with mode support
   env = Environment(mode=MODES.DEV) # Or env.mode = MODES.DEV
   
   # Set mode-specific variables
   env.set({"API_KEY": "dev-key"}, modes=[MODES.DEV])
   env.set({"API_KEY": "prod-key"}, modes=[MODES.PROD])
   
   # Access variables based on current mode
   api_key = env.get("API_KEY")  # Returns "dev-key" in DEV mode

   # Switch modes at runtime
   env.mode = MODES.PROD

   # Mode-specific decorators
   @env.mark(MODES.TEST)
   def for_test_something():
       pass # will be executed only in test mode
   
   @env.mark(MODES.PROD)
   def for_prod_something():
       pass # will be executed only in production mode

   # Context-based mode switching
   with env.with_mode(MODES.DEV):
       dev_api_key = env.get("API_KEY")  # Returns "dev-key"
   with env.with_mode(MODES.PROD):
       prod_api_key = env.get("API_KEY")  # Returns "prod-key"

   # State management
   snapshot = env.create_snapshot()
   env.rollback(snapshot)

   # Custom stage support
   env.with_stage(QA="qa", DOC="doc")
   
   @env.mark(MODES.QA)
   def for_qa_something():
       pass # will be executed only in qa mode

Community & Support
-------------------

* `GitHub Repository <https://github.com/yourusername/true-storage>`_
* `Issue Tracker <https://github.com/yourusername/true-storage/issues>`_
* `Contributing Guidelines <https://github.com/yourusername/true-storage/blob/main/CONTRIBUTING.md>`_

Indices and References
======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

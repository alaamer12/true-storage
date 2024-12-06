True Storage Documentation
==========================

.. code-block:: text
   :class: banner

   ╔════════════════════════════════════════════════════════════╗
   ║                     True Storage                           ║
   ║      Advanced Environment Management for Python            ║
   ╚════════════════════════════════════════════════════════════╝

.. image:: https://img.shields.io/badge/python-3.8%2B-blue
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :alt: MIT License
   :target: https://choosealicense.com/licenses/mit/

.. image:: https://img.shields.io/badge/pydantic-v1%20%7C%20v2-blue
   :alt: Pydantic Support

True Storage is an advanced environment management system for Python applications, offering powerful features for configuration, validation, and secure environment handling.

Key Features
------------

* **Mode-Based Configuration**: Development, testing, staging, and production environments
* **Secure Secret Management**: Safe handling of sensitive configuration
* **Variable Validation**: Type checking and custom validation rules
* **Environment Inheritance**: Hierarchical configuration management
* **Variable Interpolation**: Dynamic value resolution
* **Snapshot & Rollback**: Configuration state management
* **Pydantic Integration**: Seamless settings conversion

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

Use Cases
---------

* **Microservices**: Manage different configurations across services
* **CI/CD Pipelines**: Environment-specific testing and deployment
* **Development Teams**: Consistent configuration across team members
* **Multi-tenant Applications**: Tenant-specific environment management

Code Example
------------

.. code-block:: python

   from true_storage import Environment, MODES
   
   # Create environment with mode support
   env = Environment(mode=MODES.DEV)
   
   # Set mode-specific variables
   env.set("API_KEY", "dev-key", modes=[MODES.DEV])
   env.set("API_KEY", "prod-key", modes=[MODES.PROD])
   
   # Access variables based on current mode
   api_key = env.get("API_KEY")  # Returns "dev-key" in DEV mode

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

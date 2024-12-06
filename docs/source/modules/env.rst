Environment Module
==================

.. warning::
   For Pydantic integration with environment variables, you need to install the appropriate package:

   - For Pydantic v1: ``pip install "pydantic-settings<2.0"``
   - For Pydantic v2: ``pip install "pydantic-settings>=2.0"``

   Without this package, environment validation and type conversion features will not work.

.. module:: true_storage.env

The Environment module provides comprehensive control over environment variables with advanced features for configuration management.

Classes
-------

.. py:class:: true_storage.env.Environment
   :canonical:

   Advanced environment configuration and management system.

   This class provides a comprehensive environment variable management system with
   features like mode-specific variables, secure storage, and variable validation.

.. py:class:: true_storage.env.MODES
   :canonical:

   Environment modes for configuration management.

   This enum defines different operational modes for environment variable management,
   each with specific behaviors and access patterns.

Functions
---------

.. py:function:: true_storage.env.to_settings(env_instance: Environment, settings_class: Type[BaseSettings]) -> BaseSettings
   :canonical:

   Convert an Environment instance to a pydantic_settings v2 BaseSettings instance.
   This allows optional pydantic compatibility without modifying the core Environment class.

Exceptions
----------

.. py:exception:: true_storage.env.EnvError
   :canonical:

   Base exception for environment-related errors.

.. py:exception:: true_storage.env.ValidationError
   :canonical:

   Exception raised for environment validation errors.

.. py:exception:: true_storage.env.ModeError
   :canonical:

   Exception raised for mode-related errors.

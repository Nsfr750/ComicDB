.. _api:

API Reference
============

This document provides detailed information about the ComicDB API.

Core Modules
-----------

.. toctree::
   :maxdepth: 2

   api/modules

Core Classes
-----------

.. autosummary::
   :toctree: _autosummary
   :template: custom-module-template.rst
   :recursive:

   comicdb.models
   comicdb.database
   comicdb.reader

Database Models
--------------

.. automodule:: comicdb.models
   :members:
   :undoc-members:
   :show-inheritance:

Database Layer
-------------

.. automodule:: comicdb.database
   :members:
   :undoc-members:
   :show-inheritance:

Reader Module
------------

.. automodule:: comicdb.reader
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
---------

.. automodule:: comicdb.utils
   :members:
   :undoc-members:
   :show-inheritance:


Exceptions
----------

.. autoexception:: ComicDBError
   :members:

.. autoexception:: DatabaseError
   :members:

.. autoexception:: FileFormatError
   :members:

Constants
---------

.. automodule:: comicdb.constants
   :members:
   :show-inheritance:


Type Definitions
---------------

.. automodule:: comicdb.types
   :members:
   :show-inheritance:


Version Information
------------------

.. automodule:: comicdb.version
   :members:
   :show-inheritance:


Deprecated Features
------------------

.. deprecated:: 1.0.0
   The following features are deprecated and will be removed in a future version:
   
   - Old database schema (migrate using ``comicdb migrate``)
   - Legacy file format support

Changelog
---------

See the :doc:`changelog` for a history of changes to the API.

.. _api-versioning:

API Versioning
-------------

ComicDB follows `Semantic Versioning <https://semver.org/>`_.

- **MAJOR** version for incompatible API changes
- **MINOR** version for added functionality in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

Deprecation Policy
-----------------

1. Features will be marked as deprecated in the documentation
2. Deprecated features will continue to work for at least one minor version
3. Breaking changes will only occur in major version updates

Migration Guides
---------------

- :doc:`Upgrading to 1.0.0 </migrations/v1.0.0>`
- :doc:`Upgrading to 2.0.0 </migrations/v2.0.0>`

Testing the API
--------------

See the :doc:`testing` guide for information on testing the API.

.. note::
   Always refer to the version-specific documentation for the version you're using.
   The latest development version may include unreleased changes.

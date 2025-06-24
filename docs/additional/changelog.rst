.. _changelog:

Changelog
=========

All notable changes to ComicDB will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

`Unreleased <https://github.com/Nsfr750/ComicDB/compare/v0.0.3...HEAD>`_
------------------------------------------------------------------------

Added
~~~~~
- Initial documentation structure with Sphinx
- Basic user and developer guides
- Italian language support for documentation

Fixed
~~~~~
- Various documentation typos and formatting issues

Changed
~~~~~~~
- Updated README with new features and documentation links

`0.0.3 <https://github.com/Nsfr750/ComicDB/releases/tag/v0.0.3>`_ - 2025-06-24
------------------------------------------------------------------------------

Added
~~~~~
- Application icon support
- Basic window management
- Initial file handling

Fixed
~~~~~
- Various UI issues
- Memory leaks in file handling

`0.0.2 <https://github.com/Nsfr750/ComicDB/releases/tag/v0.0.2>`_ - 2025-05-15
------------------------------------------------------------------------------

Added
~~~~~
- Basic file opening functionality
- Image display capabilities
- Simple navigation controls

`0.0.1 <https://github.com/Nsfr750/ComicDB/releases/tag/v0.0.1>`_ - 2025-04-01
------------------------------------------------------------------------------

Added
~~~~~
- Initial project setup
- Basic project structure
- License and contribution guidelines

Versioning Policy
----------------

- **MAJOR** version for incompatible API changes
- **MINOR** version for added functionality in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

Deprecation Policy
-----------------
- Features marked as deprecated will be removed in the next MAJOR version
- Deprecation notices will be included in the changelog and documentation
- Migration guides will be provided for breaking changes

For more details, see :doc:`/developer/api`.

Generating the Changelog
-----------------------

To generate a new changelog entry:

1. Update the version in ``struttura/version.py``
2. Add a new section to this file
3. Use the following categories:
   - Added
   - Changed
   - Deprecated
   - Removed
   - Fixed
   - Security
4. Include links to relevant issues/PRs
5. Update the comparison links at the top of each version section

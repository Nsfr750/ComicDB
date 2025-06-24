.. _contributing:

Contributing to ComicDB
======================

Thank you for your interest in contributing to ComicDB! We welcome all contributions, including bug reports, feature requests, documentation improvements, and code contributions.

How to Contribute
----------------

1. **Report Bugs**
   - Check if the bug has already been reported in the `issue tracker <https://github.com/Nsfr750/ComicDB/issues>`_
   - If not, create a new issue with a clear title and description
   - Include steps to reproduce the issue and any relevant error messages

2. **Request Features**
   - Check if the feature has already been requested
   - Open an issue describing the feature and its benefits
   - Be prepared to discuss the implementation details

3. **Contribute Code**
   - Fork the repository
   - Create a feature branch (``git checkout -b feature/amazing-feature``)
   - Commit your changes (``git commit -m 'Add some amazing feature'``)
   - Push to the branch (``git push origin feature/amazing-feature``)
   - Open a Pull Request

Development Workflow
------------------

1. **Setup**
   - Follow the :doc:`installation` guide
   - Make sure all tests pass

2. **Coding Style**
   - Follow PEP 8 guidelines
   - Use type hints for all new code
   - Write docstrings for all public functions and classes

3. **Testing**
   - Write tests for new features
   - Ensure all tests pass
   - Update documentation as needed

4. **Documentation**
   - Update relevant documentation
   - Add examples for new features
   - Ensure docstrings are complete and accurate

Code Review Process
-----------------
1. Create a Pull Request (PR)
2. Ensure all CI checks pass
3. Request reviews from maintainers
4. Address review comments
5. Once approved, a maintainer will merge your PR

Coding Standards
---------------

- **Python**: Follow PEP 8
- **Documentation**: Use Google style docstrings
- **Tests**: Use pytest
- **Type Hints**: Required for all new code
- **Imports**: Grouped by standard library, third-party, and local

Commit Message Guidelines
-----------------------

Format: ``<type>(<scope>): <description>``

Types:
- feat: A new feature
- fix: A bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code changes that neither fix bugs nor add features
- test: Adding tests
- chore: Maintenance tasks

Example:

.. code-block:: text

   feat(reader): Add support for PDF files
   
   Add initial PDF support using PyPDF2. This allows users to open
   and read PDF comic books in the reader.
   
   Closes #123

Issue and PR Templates
---------------------

Please use the provided templates when creating issues and pull requests.

License
------
By contributing to ComicDB, you agree that your contributions will be licensed under the MIT License.

Code of Conduct
--------------
Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

Getting Help
-----------
If you need help or have questions, please open an issue or join our community chat.

Thank you for contributing to ComicDB!

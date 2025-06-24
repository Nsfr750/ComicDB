.. _testing:

Testing Guide
============

This guide covers how to write and run tests for the ComicDB project.

Running Tests
------------

Run all tests:

.. code-block:: bash

   pytest

Run tests with coverage:

.. code-block:: bash

   pytest --cov=comicdb tests/

Run a specific test file:

.. code-block:: bash

   pytest tests/test_models.py

Run a specific test case:

.. code-block:: bash

   pytest tests/test_models.py::TestComicModel::test_comic_creation

Test Structure
-------------

Tests are organized in the ``tests/`` directory:

.. code-block:: text

   tests/
   ├── __init__.py
   ├── conftest.py
   ├── test_models.py
   ├── test_database.py
   ├── test_reader.py
   └── integration/
       └── test_integration.py

Writing Tests
------------

1. **Unit Tests**
   - Test individual functions/methods
   - Mock external dependencies
   - Use pytest fixtures for common test data

2. **Integration Tests**
   - Test interactions between components
   - Use a test database
   - Clean up after tests

Example Test:

.. code-block:: python

   import pytest
   from comicdb.models import Comic

   class TestComicModel:
       def test_comic_creation(self):
           """Test creating a new comic."""
           comic = Comic(title="Test Comic", issue=1)
           assert comic.title == "Test Comic"
           assert comic.issue == 1

Fixtures
--------

Common fixtures are defined in ``conftest.py``:

.. code-block:: python

   import pytest
   from comicdb.database import init_db, get_session

   @pytest.fixture(scope="module")
   def test_db():
       """Set up a test database."""
       db_url = "sqlite:///:memory:"
       engine = init_db(db_url)
       session = get_session()
       yield session
       session.close()

Mocking
-------

Use the ``pytest-mock`` plugin for mocking:

.. code-block:: python

   def test_something(mocker):
       mock_func = mocker.patch('module.function')
       mock_func.return_value = 42
       
       result = function_under_test()
       
       mock_func.assert_called_once()
       assert result == 42

Test Coverage
------------

Generate a coverage report:

.. code-block:: bash

   pytest --cov=comicdb --cov-report=html tests/

Open ``htmlcov/index.html`` to view the report.

Continuous Integration
---------------------

CI runs on GitHub Actions for:
- Python 3.8, 3.9, 3.10, 3.11
- Windows, macOS, and Linux

View the CI workflow in ``.github/workflows/tests.yml``.

Testing Best Practices
---------------------

1. **Isolation**: Each test should be independent
2. **Deterministic**: Tests should produce the same results every time
3. **Descriptive**: Use clear test names and assertions
4. **Fast**: Keep tests fast to encourage frequent running
5. **Coverage**: Aim for high test coverage

Debugging Tests
--------------

Use ``pdb`` for debugging:

.. code-block:: python

   def test_something():
       import pdb; pdb.set_trace()
       # Test code here

Or use the ``--pdb`` flag to drop into the debugger on failure:

.. code-block:: bash

   pytest --pdb tests/

Performance Testing
-----------------

Use ``pytest-benchmark`` for performance testing:

.. code-block:: bash

   pip install pytest-benchmark
   pytest --benchmark-only tests/performance/

Test Data
---------

- Store test data in ``tests/data/``
- Use small, focused test files
- Include a README explaining the test data

See Also
--------
- :doc:`/developer/contributing`
- :doc:`/developer/api`

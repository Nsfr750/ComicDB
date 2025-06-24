.. _dev_installation:

Developer Installation
=====================

This guide will help you set up a development environment for ComicDB.

Prerequisites
------------
- Python 3.8 or higher
- Git
- pip (Python package installer)
- Virtual environment (recommended)

Setting Up the Development Environment
------------------------------------

1. **Fork and Clone the Repository**

   .. code-block:: bash

      # Fork the repository on GitHub
      # Then clone your fork
      git clone https://github.com/your-username/ComicDB.git
      cd ComicDB

2. **Set Up a Virtual Environment**

   .. code-block:: bash

      # Windows
      python -m venv venv
      .\venv\Scripts\activate

      # macOS/Linux
      python3 -m venv venv
      source venv/bin/activate

3. **Install Dependencies**

   .. code-block:: bash

      # Install development dependencies
      pip install -r requirements-dev.txt
      
      # Install the package in development mode
      pip install -e .


4. **Set Up Pre-commit Hooks**

   .. code-block:: bash

      pre-commit install

Running Tests
------------

Run the test suite with pytest:

.. code-block:: bash

   # Run all tests
   pytest
   
   # Run a specific test file
   pytest tests/test_models.py
   
   # Run with coverage report
   pytest --cov=comicdb tests/


Code Style
----------
We use:
- Black for code formatting
- isort for import sorting
- flake8 for linting

Run these tools before committing:

.. code-block:: bash

   black .
   isort .
   flake8

Documentation
------------
Build the documentation locally:

.. code-block:: bash

   cd docs
   make html
   # Open _build/html/index.html in your browser

Next Steps
----------
- Read the :doc:`architecture` documentation
- Check out the :doc:`contributing` guide
- Explore the :doc:`api` reference

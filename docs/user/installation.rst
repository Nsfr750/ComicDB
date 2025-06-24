.. _user_installation:

Installation
============

This guide will help you install ComicDB on your system.

Prerequisites
------------
- Python 3.8 or higher
- pip (Python package installer)

Installation Steps
-----------------

1. **Clone the repository**

   .. code-block:: bash

      git clone https://github.com/Nsfr750/ComicDB.git
      cd ComicDB

2. **Create a virtual environment (recommended)**

   .. code-block:: bash

      python -m venv venv
      .\venv\Scripts\activate  # On Windows
      source venv/bin/activate  # On macOS/Linux

3. **Install dependencies**

   .. code-block:: bash

      pip install -r requirements.txt

4. **Run the application**

   .. code-block:: bash

      python main.py

Troubleshooting
---------------

- If you encounter any issues with RAR support, make sure you have the UnRAR utility installed on your system.
- On Windows, you can download it from `WinRAR's website <https://www.win-rar.com/>`_.

Next Steps
----------
- :ref:`Quick Start Guide <quickstart>`
- :ref:`Configuration <user_configuration>`

.. _faq:

Frequently Asked Questions
=========================

Common questions and solutions for ComicDB users.

General
-------

How do I update ComicDB?
~~~~~~~~~~~~~~~~~~~~~~~~
To update ComicDB:

1. Pull the latest changes from the repository:

   .. code-block:: bash

      git pull origin main

2. Update dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

Is there a mobile version available?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Currently, ComicDB is designed for desktop platforms. A mobile version is planned for a future release.

Troubleshooting
---------------

ComicDB crashes on startup
~~~~~~~~~~~~~~~~~~~~~~~~~
Try these steps:

1. Delete the configuration file (see :ref:`Configuration <user_configuration>` for location)
2. Run with debug mode to see error messages:

   .. code-block:: bash

      python -v main.py

3. Check the log file in the configuration directory

RAR files aren't working
~~~~~~~~~~~~~~~~~~~~~~~~
Make sure you have the UnRAR utility installed:

- Windows: Install `WinRAR <https://www.win-rar.com/>`_
- macOS: ``brew install unrar``
- Linux: ``sudo apt-get install unrar`` or equivalent

Features
--------

Can I import my library from another comic reader?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yes, ComicDB supports importing from:

- ComicRack XML export
- ComicBookLover CSV export
- YACReader library

Go to File > Import to get started.

How do I organize my comics into series?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Select multiple comics in the library
2. Right-click and choose "Edit Metadata"
3. Set the same Series name for all selected comics
4. Set appropriate Volume and Issue numbers

Advanced
--------

Can I use a custom database?
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yes, you can specify a custom SQLite database path in the configuration file:

.. code-block:: ini

   [Database]
   path = /path/to/your/comics.db

How can I contribute to the project?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We welcome contributions! Please see the :doc:`Developer Documentation </developer/contributing>` for details.

Still need help?
----------------
If you can't find an answer to your question, please open an issue on our `GitHub repository <https://github.com/Nsfr750/ComicDB/issues>`_.

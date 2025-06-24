.. _user_configuration:

Configuration
=============

Learn how to customize ComicDB to suit your preferences.

Configuration Files
------------------

ComicDB stores its configuration in the following locations:

- **Windows**: ``%APPDATA%\ComicDB\config.ini``
- **macOS**: ``~/Library/Application Support/ComicDB/config.ini``
- **Linux**: ``~/.config/ComicDB/config.ini``

Basic Settings
-------------

.. code-block:: ini

   [General]
   # Language for the application interface
   language = en
   
   # Default directory for opening/saving files
   default_directory = ~/Comics
   
   # Check for updates on startup
   check_for_updates = True

Reader Settings
--------------

.. code-block:: ini

   [Reader]
   # Default reading mode (1=Single Page, 2=Double Page, 3=Webtoon)
   default_reading_mode = 1
   
   # Default zoom level (1.0 = 100%)
   default_zoom = 1.0
   
   # Show page numbers
   show_page_numbers = True
   
   # Page transition effect (none, slide, fade)
   page_transition = slide

Library Settings
---------------

.. code-block:: ini

   [Library]
   # Sort order (title, date_added, last_read, series, author)
   sort_by = title
   
   # Sort direction (asc, desc)
   sort_direction = asc
   
   # Show hidden files
   show_hidden = False

Advanced Settings
----------------

.. code-block:: ini

   [Advanced]
   # Enable debug logging
   debug = False
   
   # Maximum number of recent files to remember
   max_recent_files = 10
   
   # Custom CSS file path for theming
   # css_theme = /path/to/theme.css

Environment Variables
-------------------

You can also configure ComicDB using environment variables:

- ``COMICDB_CONFIG_DIR``: Custom configuration directory
- ``COMICDB_DEBUG``: Enable debug mode (1 or 0)
- ``COMICDB_LANGUAGE``: Set default language

Example:

.. code-block:: bash

   # Linux/macOS
   export COMICDB_DEBUG=1
   python main.py
   
   # Windows
   set COMICDB_DEBUG=1
   python main.py

Next Steps
----------
- Learn how to :ref:`install ComicDB <user_installation>`
- Check out the :ref:`FAQ <faq>` for common questions

.. _it_user_installation:

Installazione
=============

Questa guida ti aiuterà a installare ComicDB sul tuo sistema.

Prerequisiti
------------
- Python 3.8 o superiore
- pip (installer di pacchetti Python)

Passaggi per l'Installazione
---------------------------

1. **Clona il repository**

   .. code-block:: bash

      git clone https://github.com/Nsfr750/ComicDB.git
      cd ComicDB

2. **Crea un ambiente virtuale (consigliato)**

   .. code-block:: bash

      python -m venv venv
      .\venv\Scripts\activate  # Su Windows
      source venv/bin/activate  # Su macOS/Linux

3. **Installa le dipendenze**

   .. code-block:: bash

      pip install -r requirements.txt

4. **Avvia l'applicazione**

   .. code-block:: bash

      python main.py

Risoluzione dei Problemi
-----------------------

- Se riscontri problemi con il supporto RAR, assicurati di avere l'utilità UnRAR installata sul tuo sistema.
- Su Windows, puoi scaricarla dal `sito ufficiale di WinRAR <https://www.win-rar.com/>`_.

Prossimi Passi
--------------
- :ref:`Guida Rapida <it_quickstart>`
- :ref:`Configurazione <it_user_configuration>`

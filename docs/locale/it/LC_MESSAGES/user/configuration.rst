.. _it_user_configuration:

Configurazione
=============

Scopri come personalizzare ComicDB in base alle tue preferenze.

File di Configurazione
---------------------

ComicDB memorizza la configurazione nelle seguenti posizioni:

- **Windows**: ``%APPDATA%\ComicDB\config.ini``
- **macOS**: ``~/Library/Application Support/ComicDB/config.ini``
- **Linux**: ``~/.config/ComicDB/config.ini``

Impostazioni di Base
-------------------

.. code-block:: ini

   [Generale]
   # Lingua dell'interfaccia
   lingua = it
   
   # Cartella predefinita per aprire/salvare i file
   cartella_predefinita = ~/Fumetti
   
   # Controlla gli aggiornamenti all'avvio
   controlla_aggiornamenti = True

Impostazioni del Lettore
----------------------

.. code-block:: ini

   [Lettore]
   # Modalità di lettura predefinita (1=Pagina Singola, 2=Doppia Pagina, 3=Webtoon)
   modalita_lettura_predefinita = 1
   
   # Livello di zoom predefinito (1.0 = 100%)
   zoom_predefinito = 1.0
   
   # Mostra i numeri di pagina
   mostra_numeri_pagina = True
   
   # Effetto di transizione tra le pagine (nessuno, scorrimento, dissolvenza)
   effetto_transizione = scorrimento

Impostazioni della Libreria
-------------------------

.. code-block:: ini

   [Libreria]
   # Ordinamento (titolo, data_aggiunta, ultima_lettura, serie, autore)
   ordina_per = titolo
   
   # Direzione di ordinamento (crescente, decrescente)
   direzione_ordinamento = crescente
   
   # Mostra file nascosti
   mostra_nascosti = False

Impostazioni Avanzate
-------------------

.. code-block:: ini

   [Avanzate]
   # Abilita la registrazione del debug
   debug = False
   
   # Numero massimo di file recenti da ricordare
   file_recenti_massimi = 10
   
   # Percorso file CSS personalizzato per il tema
   # tema_css = /percorso/del/tema.css

Variabili d'Ambiente
------------------

Puoi anche configurare ComicDB utilizzando le variabili d'ambiente:

- ``COMICDB_CARTELLA_CONFIG``: Cartella personalizzata per la configurazione
- ``COMICDB_DEBUG``: Abilita la modalità debug (1 o 0)
- ``COMICDB_LINGUA``: Imposta la lingua predefinita

Esempio:

.. code-block:: bash

   # Linux/macOS
   export COMICDB_DEBUG=1
   python main.py
   
   # Windows
   set COMICDB_DEBUG=1
   python main.py

Prossimi Passi
--------------
- Scopri come :ref:`installare ComicDB <it_user_installation>`
- Consulta le :ref:`Domande Frequenti <it_faq>` per le domande comuni

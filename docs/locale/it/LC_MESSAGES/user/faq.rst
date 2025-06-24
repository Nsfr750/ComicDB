.. _it_faq:

Domande Frequenti
================

Domande comuni e soluzioni per gli utenti di ComicDB.

Generale
--------

Come aggiorno ComicDB?
~~~~~~~~~~~~~~~~~~~~~
Per aggiornare ComicDB:

1. Scarica le ultime modifiche dal repository:

   .. code-block:: bash

      git pull origin main

2. Aggiorna le dipendenze:

   .. code-block:: bash

      pip install -r requirements.txt

È disponibile una versione mobile?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Attualmente, ComicDB è progettato per piattaforme desktop. Una versione mobile è prevista per una prossima versione.

Risoluzione dei Problemi
----------------------

ComicDB si blocca all'avvio
~~~~~~~~~~~~~~~~~~~~~~~~~
Prova questi passaggi:

1. Elimina il file di configurazione (vedi :ref:`Configurazione <it_user_configuration>` per la posizione)
2. Esegui in modalità debug per vedere i messaggi di errore:

   .. code-block:: bash

      python -v main.py

3. Controlla il file di log nella cartella di configurazione

I file RAR non funzionano
~~~~~~~~~~~~~~~~~~~~~~~~
Assicurati di avere l'utilità UnRAR installata:

- Windows: Installa `WinRAR <https://www.win-rar.com/>`_
- macOS: ``brew install unrar``
- Linux: ``sudo apt-get install unrar`` o equivalente

Funzionalità
-----------

Posso importare la mia libreria da un altro lettore di fumetti?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sì, ComicDB supporta l'importazione da:

- Esportazione XML di ComicRack
- Esportazione CSV di ComicBookLover
- Libreria YACReader

Vai su File > Importa per iniziare.

Come posso organizzare i miei fumetti in serie?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Seleziona più fumetti nella libreria
2. Fai clic con il tasto destro e scegli "Modifica Metadati"
3. Imposta lo stesso Nome Serie per tutti i fumetti selezionati
4. Imposta i numeri di Volume e Numero appropriati

Avanzato
--------

Posso usare un database personalizzato?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sì, puoi specificare un percorso personalizzato per il database SQLite nel file di configurazione:

.. code-block:: ini

   [Database]
   percorso = /percorso/del/tuo/database.db

Come posso contribuire al progetto?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Siamo aperti ai contributi! Consulta la :doc:`Documentazione per Sviluppatori </developer/contributing>` per i dettagli.

Hai ancora bisogno di aiuto?
--------------------------
Se non trovi una risposta alla tua domanda, apri una segnalazione sul nostro `repository GitHub <https://github.com/Nsfr750/ComicDB/issues>`_.

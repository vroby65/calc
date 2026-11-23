# Manutenzione di calc

`calc` è il sorgente e l'eseguibile della calcolatrice TUI. Su Linux usa
Python 3 e il modulo standard `curses`, senza compilazione o configurazione.
Il repository contiene la copia di sviluppo da eseguire con `./calc`.

- `evaluate` calcola l'espressione e formatta il risultato. Mantieni i limiti
  agli input aritmetici, il blocco di `**` e l'isolamento dei built-in di Python.
- `press` aggiorna l'espressione e il risultato. Dopo un risultato, un operatore
  aritmetico del tastierino riprende dal valore mostrato, mentre una cifra inizia
  una nuova espressione.
- `BUTTONS` e `FOCUS` determinano la griglia e i tasti digitabili. `main` gestisce
  gli input e chiama `draw` per il display e il tastierino. L'ingresso verifica
  che stdin sia un terminale e avvia `main` tramite `curses.wrapper` per il
  ripristino del terminale all'uscita.
- `tests/test_calc.py` verifica il calcolo e lo stato del tastierino con
  `unittest`. Carica lo script senza avviare l'interfaccia.

Dalla directory del progetto:

```bash
python3 -m unittest discover -s tests -v
git diff --check
```

Per la prova interattiva, esegui `./calc` in un terminale a colori da almeno
80 colonne e 24 righe, digita `7*8`, premi Invio, verifica `56` ed esci con
`q`. Per completare una modifica, esegui i controlli pertinenti e rivedi il diff.
Aggiorna il README e questa guida quando cambiano i comandi, la struttura,
i vincoli sul comportamento o le verifiche.

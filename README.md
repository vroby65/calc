# calc

Calcolatrice da terminale con display e tastierino. Su Linux usa Python 3
con il modulo standard `curses` e un terminale a colori con supporto Unicode.

Per avviare la copia di sviluppo, entra nella directory del progetto ed esegui:

```bash
./calc
```

- Digita un'espressione, per esempio `(7+1)*8`, e premi Invio oppure `=`.
- Usa le frecce per selezionare un tasto e Spazio per premerlo.
- Usa `C` per azzerare e Backspace per cancellare l'ultimo carattere.
- Premi `q` o Esc per uscire.

Il comando già installato sul PC si trova in `/usr/local/bin/calc`.

Per eseguire i test dalla directory del progetto:

```bash
python3 -m unittest discover -s tests -v
```

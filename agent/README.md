# Maintenance guide

`calc` is both the Bash source and the executable. It uses `stty` and ANSI
escape sequences for the terminal, and GNU `bc` for decimal arithmetic.
Run the development copy with `./calc`.

- `parse_expression` recognizes numeric literals and applies operator
  precedence. `evaluate` passes the reconstructed expression to `bc`,
  reports errors, and formats the result. Reject `**` and tokens outside the
  arithmetic grammar.
- `press` updates the expression and displayed result. After evaluation,
  an arithmetic operator continues from the displayed value and a digit
  starts a new expression.
- `buttons` defines the keypad and its recognized labels. `read_key` reads
  keys and ANSI sequences, including SGR mouse events. `main` and `draw`
  share keypad geometry for hit testing and focus movement. `draw` writes
  within the upper-left frame on the current screen.
- The `Q` button and `q` shortcut use the same clear-and-quit path. On exit,
  restore the saved `stty` settings, show the cursor, and disable mouse
  reporting.
- `tests/test_calc.py` sources the Bash functions for arithmetic checks and
  drives the executable through a pseudoterminal for interaction tests.

From the repository root, check Bash syntax, run the tests, and verify the diff.

```bash
bash -n calc
python3 -m unittest discover -s tests -v
git diff --check
```

For a manual check, run `./calc` in a color terminal with at least 36 columns
and 22 rows. Enter `7*8` using a mix of clicks and arrow keys with Space,
then press Enter and confirm `56`. Activate `Q` to check that it clears the
screen. Review the diff and run the relevant checks before finishing.
Update the README and this guide when commands, structure, behavior
invariants, or verification steps change.

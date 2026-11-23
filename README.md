# calc

A Bash calculator for the Linux terminal. The display and keypad sit in the
upper-left corner, leaving the surrounding terminal content visible. The
palette follows `fm`, with dark gray panels, muted yellow labels, a bright
yellow result, and a teal focus highlight.

## Run

You need Bash, `stty`, GNU `bc`, and a terminal with ANSI 256-color and
Unicode support. The calculator uses 36 columns and 22 rows.

Download the script and make it executable.

```bash
curl -fsSL https://raw.githubusercontent.com/vroby65/calc/main/calc -o calc && chmod +x calc
```

Run it with `./calc`. To get the tests too, clone the repository.

```bash
git clone https://github.com/vroby65/calc.git
cd calc
./calc
```

Install `calc` in your user bin directory with this command.

```bash
install -Dm755 calc "$HOME/.local/bin/calc"
```

Run `calc` from anywhere when `~/.local/bin` is on your `PATH`.

## Controls

- Type an expression such as `(7+1)*8` and press Enter or `=` to evaluate it.
- Use the arrow keys to move focus and Space to press the selected button.
- Left-click a button to press it. Mouse input uses SGR mouse reporting.
- Press `C` to reset the display. Press Backspace or use `DEL` to delete the
  last character.
- Click `Q` or press `q` to quit and clear the screen. Esc and Ctrl+C quit
  while leaving the screen contents visible.

Division uses 30 decimal places internally. The display rounds results to
at most 10 digits after the decimal point.

## Tests

Run the checks from the repository root. The tests require Python 3.11 or newer.

```bash
bash -n calc
python3 -m unittest discover -s tests -v
```

import os
import pty
import select
import signal
import subprocess
import termios
import time
import unittest
from contextlib import contextmanager
from pathlib import Path


CALC = Path(__file__).resolve().parents[1] / "calc"
FRAME_TOP = "\x1b[1;1H┌──────────────────────────────────┐".encode()
FRAME_END = "\x1b[22;1H└──────────────────────────────────┘".encode()
MOUSE_ON = b"\x1b[?1000h\x1b[?1006h"
TERMINAL_RESTORED = b"\x1b[?1000l\x1b[?1006l\x1b[?25h"
CLEAR_SCREEN = b"\x1b[2J\x1b[H"


def run_shell(code, *args):
    return subprocess.run(
        ["bash", "-c", 'source "$1"; shift; ' + code, "test", CALC, *args],
        capture_output=True,
        text=True,
        timeout=4,
        check=True,
    ).stdout


def evaluate(expression):
    return run_shell('evaluate "$1"', expression).strip()


def press(label, entry, shown):
    updated, result = run_shell(
        'entry=$2; shown=$3; press "$1"; printf "%s\\n%s\\n" "$entry" "$shown"',
        label,
        entry,
        shown or "",
    ).splitlines()
    return updated, result or None


class CalcTests(unittest.TestCase):
    def test_arithmetic_and_result_formatting(self):
        for expression, result in (
            ("2+3*4", "14"),
            ("(2+3)*4", "20"),
            ("8/2", "4"),
            ("1/3", "0.3333333333"),
            ("2/3", "0.6666666667"),
            ("1--2*+3", "7"),
            ("-7//3", "-3"),
            ("7%-3", "-2"),
            ("0.5%0.3", "0.2"),
            ("9223372036854775808+1", "9223372036854775809"),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(evaluate(expression), result)

    def test_invalid_expressions(self):
        for expression in ("", "1+", "1/0", "2**3", "abs(1)", "2^3", "1;2", "1\n2"):
            with self.subTest(expression=expression):
                self.assertEqual(evaluate(expression), "Error")

    def test_ignores_bc_options_in_environment(self):
        output = run_shell('export POSIXLY_CORRECT=1 BC_ENV_ARGS=-s; evaluate "2/3"')
        self.assertEqual(output.strip(), "0.6666666667")

    def test_result_can_start_a_new_calculation(self):
        entry, shown = press("=", "2+3", None)
        self.assertEqual((entry, shown), ("2+3", "5"))
        self.assertEqual(press("*", entry, shown), ("5*", None))
        self.assertEqual(press("7", entry, shown), ("7", None))

    def test_clear_and_delete(self):
        self.assertEqual(press("DEL", "123", None), ("12", None))
        self.assertEqual(press("C", "2+3", "5"), ("", None))


@contextmanager
def terminal(rows=24, columns=80, term="xterm-256color"):
    master, slave = pty.openpty()
    try:
        termios.tcsetwinsize(slave, (rows, columns))
        initial_settings = termios.tcgetattr(slave)
        env = dict(os.environ, TERM=term, LC_ALL="C.UTF-8")
        with subprocess.Popen(
            [CALC], stdin=slave, stdout=slave, stderr=slave, env=env
        ) as process:
            try:
                yield master, slave, process, initial_settings
            finally:
                if process.poll() is None:
                    process.kill()
    finally:
        os.close(master)
        os.close(slave)


class TerminalTests(unittest.TestCase):
    def read_until(self, master, expected):
        output = bytearray()
        deadline = time.monotonic() + 4
        while expected not in output:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([master], [], [], remaining)[0]:
                self.fail(f"{expected!r} missing from terminal output: {output!r}")
            output.extend(os.read(master, 8192))
        return output

    def test_left_frame_preserves_screen_until_q(self):
        with terminal() as (master, slave, process, settings):
            opened = self.read_until(master, FRAME_END)
            self.assertIn(MOUSE_ON, opened)
            self.assertIn(b"\x1b[38;5;144;48;5;237m" + FRAME_TOP, opened)
            self.assertIn(b"\x1b[1;33;48;5;237m" + b"0".rjust(30), opened)
            self.assertNotIn(b"\x1b[2J", opened)
            self.assertNotIn(b"\x1b[?1049", opened)
            self.assertNotIn(b"arrows:", opened)

            os.write(master, b"7")
            updated = self.read_until(master, FRAME_END)
            self.assertNotIn(b"\x1b[2J", updated)

            os.write(master, b"q")
            self.assertEqual(process.wait(timeout=4), 0)
            self.assertEqual(termios.tcgetattr(slave), settings)
            self.assertIn(CLEAR_SCREEN, self.read_until(master, TERMINAL_RESTORED))

    def test_keyboard_calculation_and_result_reuse(self):
        with terminal() as (master, slave, process, settings):
            self.read_until(master, FRAME_END)
            os.write(master, b"7*8\r")
            self.read_until(master, b"56")
            os.write(master, b"+123\x7f\r")
            self.read_until(master, b"68")
            os.write(master, b"q")
            self.assertEqual(process.wait(timeout=4), 0)
            self.assertEqual(termios.tcgetattr(slave), settings)

    def test_arrows_space_and_escape(self):
        with terminal() as (master, slave, process, settings):
            self.read_until(master, FRAME_END)
            # 8 → DEL → C → ) → / → 7
            os.write(master, b"\x1bOA\x1bOD\x1b[D\x1b[B\x1b[C *9\r")
            self.read_until(master, b"63")
            os.write(master, b"\x1b")
            self.assertEqual(process.wait(timeout=4), 0)
            self.assertEqual(termios.tcgetattr(slave), settings)
            self.assertNotIn(b"\x1b[2J", self.read_until(master, TERMINAL_RESTORED))

    def test_mouse_clicks_and_keyboard_share_the_focus(self):
        with terminal() as (master, _, process, _):
            self.read_until(master, FRAME_END)
            os.write(
                master,
                b"\x1b[<0;2;11M\x1b[<0;36;11M\x1b[<0;6;6M\x1b[<0;6;22M"
                b"\x1b[<2;14;11M\x1b[<0;6;11M\x1b[<0;6;11m"
                b"\x1b[C \x1b[<0;30;20M\x1b[<0;22;11M\x1b[<0;22;20M",
            )
            self.read_until(master, b"87\x1b[0m")
            os.write(master, b"q")
            self.assertEqual(process.wait(timeout=4), 0)

    def test_quit_button_click_clears_screen(self):
        with terminal() as (master, slave, process, settings):
            opened = self.read_until(master, FRAME_END)
            self.assertIn(b"[  \x1b[1mQ\x1b[22m   ]", opened)
            os.write(master, b"\x1b[<0;30;6M")
            self.assertEqual(process.wait(timeout=4), 0)
            self.assertEqual(termios.tcgetattr(slave), settings)
            self.assertIn(CLEAR_SCREEN, self.read_until(master, TERMINAL_RESTORED))

    def test_quit_button_can_be_focused_with_arrows(self):
        with terminal() as (master, _, process, _):
            self.read_until(master, FRAME_END)
            # 8 → 9 → / → ) → Q
            os.write(master, b"\x1b[C\x1b[C\x1b[A\x1b[A")
            self.read_until(master, b"\x1b[38;5;252;48;5;23m[  \x1b[1mQ")
            os.write(master, b" ")
            self.assertEqual(process.wait(timeout=4), 0)
            self.assertIn(CLEAR_SCREEN, self.read_until(master, TERMINAL_RESTORED))

    def test_resize_from_small_terminal(self):
        with terminal(10, 40) as (master, slave, process, _):
            small = self.read_until(master, MOUSE_ON)
            self.assertNotIn(b"Terminal too small", small)
            self.assertNotIn(FRAME_TOP, small)
            termios.tcsetwinsize(slave, (24, 80))
            process.send_signal(signal.SIGWINCH)
            resized = self.read_until(master, FRAME_END)
            self.assertIn(FRAME_TOP, resized)
            self.assertNotIn(b"\x1b[2J", resized)
            os.write(master, b"q")
            self.assertEqual(process.wait(timeout=4), 0)

    def test_runs_without_terminfo_and_restores_terminal_on_ctrl_c(self):
        with terminal(term="calc-test-no-terminfo") as (master, slave, process, settings):
            self.read_until(master, FRAME_END)
            os.write(master, b"\x1b[C *9\n")
            self.read_until(master, b"81")
            os.write(master, b"\x03")
            self.assertEqual(process.wait(timeout=4), 0)
            self.assertEqual(termios.tcgetattr(slave), settings)
            self.read_until(master, TERMINAL_RESTORED)

    def test_restores_terminal_on_sigterm(self):
        with terminal() as (master, slave, process, settings):
            self.read_until(master, FRAME_END)
            process.send_signal(signal.SIGTERM)
            self.assertEqual(process.wait(timeout=4), 143)
            self.assertEqual(termios.tcgetattr(slave), settings)
            self.read_until(master, TERMINAL_RESTORED)

    def test_refuses_noninteractive_input(self):
        result = subprocess.run(
            [CALC], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=4
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), "Run calc in a terminal.")

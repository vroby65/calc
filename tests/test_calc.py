import runpy
import unittest
from pathlib import Path


calc = runpy.run_path(str(Path(__file__).resolve().parents[1] / "calc"))
evaluate = calc["evaluate"]
press = calc["press"]


class CalcTests(unittest.TestCase):
    def test_arithmetic_and_result_formatting(self):
        for expression, result in (
            ("2+3*4", "14"),
            ("(2+3)*4", "20"),
            ("8/2", "4"),
            ("1/3", "0.3333333333"),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(evaluate(expression), result)

    def test_invalid_expressions(self):
        for expression in ("", "1+", "1/0", "2**3", "abs(1)"):
            with self.subTest(expression=expression):
                self.assertEqual(evaluate(expression), "Error")

    def test_result_can_start_a_new_calculation(self):
        entry, shown = press("=", "2+3", None)
        self.assertEqual((entry, shown), ("2+3", "5"))
        self.assertEqual(press("*", entry, shown), ("5*", None))
        self.assertEqual(press("7", entry, shown), ("7", None))

    def test_clear_and_delete(self):
        self.assertEqual(press("DEL", "123", None), ("12", None))
        self.assertEqual(press("C", "2+3", "5"), ("", None))

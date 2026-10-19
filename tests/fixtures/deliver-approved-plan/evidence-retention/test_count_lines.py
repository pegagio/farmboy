"""Copy with input.txt/expected.txt into the disposable toy project's tests/."""
from pathlib import Path
import unittest

from count_lines import count_lines


class CountLinesTests(unittest.TestCase):
    def test_controlled_input(self):
        fixtures = Path(__file__).parent
        text = (fixtures / "input.txt").read_text(encoding="utf-8")
        expected = int((fixtures / "expected.txt").read_text(encoding="utf-8"))
        self.assertEqual(count_lines(text), expected)

    def test_empty(self):
        self.assertEqual(count_lines(""), 0)

    def test_last_line_without_newline(self):
        self.assertEqual(count_lines("alpha\nbeta"), 2)


if __name__ == "__main__":
    unittest.main()

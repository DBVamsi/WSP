import unittest
import sys
import os

# Add the parent directory to the Python path to allow importing from game_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_engine.input_parser import parse_input

class TestInputParser(unittest.TestCase):
    """
    Test suite for the parse_input function from input_parser.
    """

    def test_parse_input_returns_raw_text(self):
        """
        Tests if parse_input currently returns the raw text input unchanged.
        This is because it's a placeholder function.
        """
        test_cases = [
            "look north",
            "GET SWORD",
            "  examine chest  ",
            "",
            "a b c d e f g",
            "12345",
            "!@#$%^"
        ]

        for text_input in test_cases:
            with self.subTest(input=text_input):
                self.assertEqual(parse_input(text_input), text_input,
                                 f"parse_input should return the raw text '{text_input}' but did not.")

if __name__ == '__main__':
    unittest.main()

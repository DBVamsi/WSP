import unittest
import sys
import os

# Add the parent directory to the Python path to allow importing from game_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_engine.input_parser import parse_input

class TestInputParser(unittest.TestCase):
    """
    Test suite for the parse_input function from game_engine.input_parser.
    """

    def test_normal_input(self):
        """Test with a typical command and argument."""
        result = parse_input("look around")
        self.assertEqual(result, {"command": "look", "arguments": ["around"]})

    def test_input_with_extra_spaces(self):
        """Test input with leading, trailing, and multiple internal spaces."""
        result = parse_input("  take   potion  ")
        self.assertEqual(result, {"command": "take", "arguments": ["potion"]})

    def test_input_with_mixed_case(self):
        """Test input with mixed uppercase and lowercase letters."""
        result = parse_input("GO NORTH")
        self.assertEqual(result, {"command": "go", "arguments": ["north"]})

    def test_command_only(self):
        """Test input with only a command and no arguments."""
        result = parse_input("inventory")
        self.assertEqual(result, {"command": "inventory", "arguments": []})

    def test_empty_input(self):
        """Test input that is an empty string."""
        result = parse_input("")
        self.assertEqual(result, {"command": None, "arguments": []})

    def test_whitespace_only_input(self):
        """Test input that consists only of whitespace."""
        result = parse_input("   ")
        self.assertEqual(result, {"command": None, "arguments": []})
        result_tab = parse_input("\t\t")
        self.assertEqual(result_tab, {"command": None, "arguments": []})

    def test_input_with_multiple_arguments(self):
        """Test input with a command and multiple arguments."""
        result = parse_input("use healing herb self")
        self.assertEqual(result, {"command": "use", "arguments": ["healing", "herb", "self"]})

    def test_single_word_command_mixed_case_and_spaces(self):
        """Test a single command word with mixed case and surrounding spaces."""
        result = parse_input("  ATTACK   ")
        self.assertEqual(result, {"command": "attack", "arguments": []})

if __name__ == '__main__':
    unittest.main()

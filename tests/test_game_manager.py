import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tkinter as tk # Imported for type hinting and context, but will be mocked

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_engine.game_manager import GameManager
# GameUI is imported by game_manager, so it needs to be mockable if game_manager is loaded
# from ui.ui_manager import GameUI # Not strictly needed if GameUI is fully mocked

class TestGameManager(unittest.TestCase):
    """
    Test suite for the GameManager class.
    """

    @patch('game_engine.game_manager.os.path.exists')
    @patch('game_engine.game_manager.setup_database')
    @patch('game_engine.game_manager.GameUI')
    @patch('game_engine.game_manager.tk.Tk')
    def test_game_manager_initialization(self, mock_tk_class, mock_game_ui_class, 
                                         mock_setup_database, mock_os_path_exists):
        """
        Tests the initialization of GameManager, ensuring dependencies are called.
        Mock order (from @patch decorators): tk.Tk, GameUI, setup_database, os.path.exists
        Test method args order: mock_tk_class, mock_game_ui_class, mock_setup_database, mock_os_path_exists
        """
        # Ensure os.path.exists returns True to simplify the data directory check
        mock_os_path_exists.return_value = True

        # Instantiate GameManager
        game_manager = GameManager()

        # Assertions
        mock_os_path_exists.assert_called_once_with('data')
        mock_setup_database.assert_called_once()
        mock_tk_class.assert_called_once()
        
        # GameUI should be initialized with the instance returned by tk.Tk()
        mock_game_ui_class.assert_called_once_with(mock_tk_class.return_value)
        
        self.assertEqual(game_manager.root, mock_tk_class.return_value,
                         "GameManager's root is not the instance returned by tk.Tk mock.")
        self.assertEqual(game_manager.ui, mock_game_ui_class.return_value,
                         "GameManager's ui is not the instance returned by GameUI mock.")

    @patch('game_engine.game_manager.os.path.exists')
    @patch('game_engine.game_manager.setup_database')
    @patch('game_engine.game_manager.GameUI')
    @patch('game_engine.game_manager.tk.Tk')
    def test_start_game_calls_ui_start_ui(self, mock_tk_class, mock_game_ui_class,
                                           mock_setup_database, mock_os_path_exists):
        """
        Tests if GameManager.start_game() correctly calls the ui's start_ui() method.
        Mock order (from @patch decorators): tk.Tk, GameUI, setup_database, os.path.exists
        Test method args order: mock_tk_class, mock_game_ui_class, mock_setup_database, mock_os_path_exists
        """
        mock_os_path_exists.return_value = True

        # Mock the GameUI instance and its start_ui method
        mock_ui_instance = MagicMock()
        mock_game_ui_class.return_value = mock_ui_instance

        # Instantiate GameManager
        game_manager = GameManager()

        # Call the method to test
        game_manager.start_game()

        # Assert that the UI's start_ui method was called
        mock_ui_instance.start_ui.assert_called_once()
        
        # Also check that core init steps were still performed
        mock_setup_database.assert_called_once()
        mock_tk_class.assert_called_once()
        mock_game_ui_class.assert_called_once_with(mock_tk_class.return_value)


if __name__ == '__main__':
    unittest.main()

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

    @patch('game_engine.game_manager.tk.Tk')
    @patch('game_engine.game_manager.GameUI')
    @patch('game_engine.game_manager.setup_database')
    @patch('game_engine.game_manager.os.path.exists')
    @patch('game_engine.game_manager.AIDungeonMaster')
    def test_game_manager_initialization(self, mock_aidm_class, mock_os_path_exists, 
                                         mock_setup_database, mock_game_ui_class, mock_tk_class):
        """
        Tests the initialization of GameManager, ensuring dependencies are called.
        Order of args should match the reverse order of decorators.
        """
        mock_os_path_exists.return_value = True
        mock_aidm_instance = MagicMock()
        mock_aidm_class.return_value = mock_aidm_instance

        game_manager = GameManager()

        mock_os_path_exists.assert_called_once_with('data')
        mock_setup_database.assert_called_once()
        mock_tk_class.assert_called_once()
        mock_game_ui_class.assert_called_once_with(mock_tk_class.return_value, game_manager)
        mock_aidm_class.assert_called_once_with(api_key='YOUR_GOOGLE_AI_API_KEY_PLACEHOLDER')
        
        self.assertEqual(game_manager.root, mock_tk_class.return_value)
        self.assertEqual(game_manager.ui, mock_game_ui_class.return_value)
        self.assertEqual(game_manager.ai_dm, mock_aidm_instance)

    @patch('game_engine.game_manager.tk.Tk')
    @patch('game_engine.game_manager.GameUI')
    @patch('game_engine.game_manager.setup_database')
    @patch('game_engine.game_manager.os.path.exists')
    @patch('game_engine.game_manager.AIDungeonMaster')
    def test_start_game_calls_ui_start_ui_and_ai_dm(self, mock_aidm_class, mock_os_path_exists,
                                           mock_setup_database, mock_game_ui_class, mock_tk_class):
        """
        Tests if GameManager.start_game() calls AI DM for initial scene,
        adds it to UI, and then starts the UI.
        """
        mock_os_path_exists.return_value = True
        
        mock_ui_instance = MagicMock()
        mock_game_ui_class.return_value = mock_ui_instance
        
        mock_aidm_instance = MagicMock()
        mock_aidm_class.return_value = mock_aidm_instance
        mock_aidm_instance.get_initial_scene_description.return_value = "Test initial scene."

        game_manager = GameManager()

        game_manager.start_game()

        mock_aidm_instance.get_initial_scene_description.assert_called_once()
        mock_ui_instance.add_story_text.assert_any_call("Test initial scene.")
        mock_ui_instance.start_ui.assert_called_once()
        
        # Verify init calls still happened
        mock_setup_database.assert_called_once()
        mock_tk_class.assert_called_once()
        mock_game_ui_class.assert_called_once_with(mock_tk_class.return_value, game_manager)
        mock_aidm_class.assert_called_once_with(api_key='YOUR_GOOGLE_AI_API_KEY_PLACEHOLDER')


    @patch('game_engine.game_manager.tk.Tk')
    @patch('game_engine.game_manager.GameUI')
    @patch('game_engine.game_manager.setup_database')
    @patch('game_engine.game_manager.os.path.exists')
    @patch('game_engine.game_manager.AIDungeonMaster')
    @patch('game_engine.game_manager.parse_input')
    def test_process_player_command_with_input(self, mock_parse_input, mock_aidm_class, 
                                               mock_os_path_exists, mock_setup_database, 
                                               mock_game_ui_class, mock_tk_class):
        mock_os_path_exists.return_value = True
        mock_ui_instance = MagicMock()
        mock_game_ui_class.return_value = mock_ui_instance
        # AIDM is initialized but not directly used in this method by current design
        mock_aidm_instance = MagicMock()
        mock_aidm_class.return_value = mock_aidm_instance
        
        mock_ui_instance.get_player_input.return_value = "test command"
        mock_parse_input.return_value = "parsed test command"

        manager = GameManager()
        manager.process_player_command()

        mock_ui_instance.get_player_input.assert_called_once()
        mock_parse_input.assert_called_once_with("test command")
        mock_aidm_class.assert_called_once() # Ensure AIDM was still initialized
        
        calls = mock_ui_instance.add_story_text.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0][0], 'You typed: test command')
        self.assertEqual(calls[1][0][0], 'The ancient echoes respond...')

    @patch('game_engine.game_manager.tk.Tk')
    @patch('game_engine.game_manager.GameUI')
    @patch('game_engine.game_manager.setup_database')
    @patch('game_engine.game_manager.os.path.exists')
    @patch('game_engine.game_manager.AIDungeonMaster')
    @patch('game_engine.game_manager.parse_input')
    def test_process_player_command_empty_input(self, mock_parse_input, mock_aidm_class, 
                                                mock_os_path_exists, mock_setup_database, 
                                                mock_game_ui_class, mock_tk_class):
        mock_os_path_exists.return_value = True
        mock_ui_instance = MagicMock()
        mock_game_ui_class.return_value = mock_ui_instance
        mock_aidm_instance = MagicMock()
        mock_aidm_class.return_value = mock_aidm_instance
        
        mock_ui_instance.get_player_input.return_value = "   " 

        manager = GameManager()
        manager.process_player_command()

        mock_ui_instance.get_player_input.assert_called_once()
        mock_ui_instance.add_story_text.assert_not_called()
        mock_parse_input.assert_not_called()
        mock_aidm_class.assert_called_once() # Ensure AIDM was still initialized


if __name__ == '__main__':
    unittest.main()

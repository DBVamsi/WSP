import unittest
from unittest.mock import MagicMock # Patch is not strictly needed if we pass mocks directly
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the handler functions and the descriptions dictionary directly
from main_eel_handlers import (
    js_ready_handler,
    process_player_command_handler,
    handle_map_click_handler,
    MAP_REGION_DESCRIPTIONS
)

class TestMainEelHandlers(unittest.TestCase):
    """
    Test suite for handler functions in main_eel_handlers.py.
    """

    def setUp(self):
        self.mock_web_ui_manager = MagicMock()
        self.mock_game_manager = MagicMock()
        # Reset is_ready for each test if it's stateful across calls within a test
        self.mock_web_ui_manager.is_ready = True

    def test_handle_map_click_handler_known_region(self):
        """Tests handle_map_click_handler with a known region name."""
        region_name = "The Old Well"
        expected_description = MAP_REGION_DESCRIPTIONS[region_name]
        expected_message = f"You focus your attention on {region_name}.\n{expected_description}"

        result = handle_map_click_handler(region_name, self.mock_web_ui_manager, MAP_REGION_DESCRIPTIONS)

        self.mock_web_ui_manager.add_story_text.assert_called_once_with(expected_message)
        self.assertEqual(result, f"Information for '{region_name}' displayed (from handler).")

    def test_handle_map_click_handler_unknown_region(self):
        """Tests handle_map_click_handler with an unknown region name."""
        region_name = "The Mysterious Void"
        expected_message = f"You focus your attention on {region_name}.\nYou clicked on '{region_name}', but there's nothing more to see here right now."

        result = handle_map_click_handler(region_name, self.mock_web_ui_manager, MAP_REGION_DESCRIPTIONS)

        self.mock_web_ui_manager.add_story_text.assert_called_once_with(expected_message)
        self.assertEqual(result, f"Information for '{region_name}' displayed (from handler).")

    def test_handle_map_click_handler_ui_not_ready(self):
        """Tests handle_map_click_handler when UI is not ready."""
        self.mock_web_ui_manager.is_ready = False
        region_name = "The Old Well"

        # We expect a print to console (which we can't easily check here without more patching)
        # and add_story_text not to be called.
        with patch('builtins.print') as mock_print: # Check console output for the warning
            result = handle_map_click_handler(region_name, self.mock_web_ui_manager, MAP_REGION_DESCRIPTIONS)
            self.mock_web_ui_manager.add_story_text.assert_not_called()
            # Check if the warning print was called
            mock_print.assert_any_call(f"Handler Warning: WebUIManager not ready or None. Cannot send map click message to UI: You focus your attention on {region_name}.\n{MAP_REGION_DESCRIPTIONS[region_name]}")
        self.assertEqual(result, f"Information for '{region_name}' displayed (from handler).")


    def test_process_player_command_handler(self):
        """Tests process_player_command_handler."""
        command = "look around"

        process_player_command_handler(command, self.mock_game_manager)

        self.mock_game_manager.process_player_command_from_js.assert_called_once_with(command)

    def test_js_ready_handler(self):
        """Tests the js_ready_handler function."""
        message = "JavaScript is ready!"

        js_ready_handler(message, self.mock_web_ui_manager, self.mock_game_manager)

        self.mock_web_ui_manager.set_ready.assert_called_once()
        self.mock_game_manager.initialize_game_state_and_ui.assert_called_once()

    def test_js_ready_handler_no_game_manager(self):
        """Tests js_ready_handler if game_manager is None."""
        message = "JS ready, GM None"
        with patch('builtins.print') as mock_print:
            js_ready_handler(message, self.mock_web_ui_manager, None)
            self.mock_web_ui_manager.set_ready.assert_called_once()
            mock_print.assert_any_call("Handler Error: game_manager_instance is None in js_ready_handler")


if __name__ == '__main__':
    unittest.main()

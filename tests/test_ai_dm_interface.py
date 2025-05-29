import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path to allow importing from game_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_engine.ai_dm_interface import AIDungeonMaster

class TestAIDungeonMaster(unittest.TestCase):
    """
    Test suite for the AIDungeonMaster class.
    """

    @patch('game_engine.ai_dm_interface.genai')
    def test_init_with_direct_api_key(self, mock_genai):
        """
        Tests initialization with a directly provided API key.
        """
        dm = AIDungeonMaster(api_key='direct_test_key')
        mock_genai.configure.assert_called_once_with(api_key='direct_test_key')
        mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-flash-latest')
        self.assertEqual(dm.model, mock_genai.GenerativeModel.return_value)

    @patch('game_engine.ai_dm_interface.os.getenv')
    @patch('game_engine.ai_dm_interface.genai')
    def test_init_with_env_variable_api_key(self, mock_genai, mock_os_getenv):
        """
        Tests initialization with API key from environment variable.
        """
        mock_os_getenv.return_value = 'env_test_key'
        dm = AIDungeonMaster() # No api_key argument
        mock_os_getenv.assert_called_once_with("GOOGLE_API_KEY")
        mock_genai.configure.assert_called_once_with(api_key='env_test_key')
        mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-flash-latest')
        self.assertEqual(dm.model, mock_genai.GenerativeModel.return_value)

    @patch('game_engine.ai_dm_interface.os.getenv')
    @patch('game_engine.ai_dm_interface.genai') # Still need to mock genai to prevent actual calls
    def test_init_no_api_key_raises_value_error(self, mock_genai, mock_os_getenv):
        """
        Tests that ValueError is raised if no API key is provided or found in env.
        """
        mock_os_getenv.return_value = None # Simulate no environment variable
        with self.assertRaises(ValueError) as context:
            AIDungeonMaster() # No api_key argument
        self.assertTrue("API key not provided" in str(context.exception))
        mock_genai.configure.assert_not_called() # Ensure configure wasn't called

    @patch('game_engine.ai_dm_interface.genai')
    def test_get_initial_scene_description_success(self, mock_genai_module):
        """
        Tests successful retrieval of an initial scene description.
        """
        # Mock the GenerativeModel instance that __init__ creates
        mock_model_instance = MagicMock()
        mock_genai_module.GenerativeModel.return_value = mock_model_instance

        # Mock the response from generate_content
        mock_response = MagicMock()
        mock_response.text = "A mystical forest appears before you."
        mock_model_instance.generate_content.return_value = mock_response

        dm = AIDungeonMaster(api_key='test_key_success') # api_key is needed for init
        scene = dm.get_initial_scene_description()

        # Check that generate_content was called (can also check prompt if needed)
        mock_model_instance.generate_content.assert_called_once() 
        # Example of checking the prompt:
        # expected_prompt_part = 'You are a Dungeon Master'
        # called_prompt = mock_model_instance.generate_content.call_args[0][0]
        # self.assertIn(expected_prompt_part, called_prompt)
        
        self.assertEqual(scene, "A mystical forest appears before you.")

    @patch('builtins.print') # Mock the print function
    @patch('game_engine.ai_dm_interface.genai')
    def test_get_initial_scene_description_api_error(self, mock_genai_module, mock_print):
        """
        Tests the API error handling in get_initial_scene_description.
        """
        mock_model_instance = MagicMock()
        mock_genai_module.GenerativeModel.return_value = mock_model_instance

        # Configure generate_content to raise an exception
        api_error_message = "Simulated API error"
        mock_model_instance.generate_content.side_effect = Exception(api_error_message)

        dm = AIDungeonMaster(api_key='test_key_error')
        scene = dm.get_initial_scene_description()

        self.assertEqual(scene, 'Error: The mists of creation obscure your vision... Please check your connection or API key.')
        mock_print.assert_called_once_with(f'Error contacting AI DM for initial scene: {api_error_message}')

if __name__ == '__main__':
    unittest.main()

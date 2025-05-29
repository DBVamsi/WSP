import unittest
import tkinter as tk
import sys
import os

# Add the parent directory to the Python path to allow importing from ui
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.ui_manager import GameUI

class TestGameUI(unittest.TestCase):
    """
    Test suite for the GameUI class.
    """

    def setUp(self):
        """
        Set up the test environment before each test.
        Creates a root Tk window and a GameUI instance.
        """
        self.root = tk.Tk()
        self.root.withdraw() # Hide the window during tests
        self.app_ui = GameUI(self.root)
        self.root.update_idletasks() # Process pending tasks like geometry and title

    def tearDown(self):
        """
        Clean up the test environment after each test.
        Destroys the root Tk window.
        """
        self.root.destroy()

    def test_gameui_instance_creation(self):
        """
        Tests if the GameUI instance is created successfully.
        """
        self.assertIsInstance(self.app_ui, GameUI, "app_ui is not an instance of GameUI.")

    def test_window_title(self):
        """
        Tests if the window title is set correctly.
        """
        self.assertEqual(self.app_ui.root.title(), 'Mythic Realms RPG', "Window title is not correct.")

    def test_window_geometry(self):
        """
        Tests if the window geometry is set correctly.
        winfo_geometry() returns WxH+X+Y, so we check if our dimension is in it.
        """
        # update_idletasks in setUp should be enough, but one more here won't hurt
        # for geometry which can be particularly dependent on window manager interactions.
        self.root.update() 
        self.assertIn('1000x700', self.app_ui.root.winfo_geometry(), "Window geometry is not correct.")

    def test_frames_creation(self):
        """
        Tests if the main UI frames (stats, story, input) are created as tk.Frame instances.
        """
        self.assertIsInstance(self.app_ui.stats_frame, tk.Frame, "stats_frame is not a tk.Frame.")
        self.assertIsInstance(self.app_ui.story_frame, tk.Frame, "story_frame is not a tk.Frame.")
        self.assertIsInstance(self.app_ui.input_frame, tk.Frame, "input_frame is not a tk.Frame.")

    def test_widget_creation_and_properties(self):
        """
        Tests if the UI widgets (labels, text area, entry, button) are created correctly
        and have the specified properties.
        """
        # Stats Label
        self.assertIsInstance(self.app_ui.stats_label, tk.Label, "stats_label is not a tk.Label.")
        self.assertEqual(self.app_ui.stats_label.cget('text'), 'Stats Go Here', "stats_label text is incorrect.")

        # Story Text Area (replaces story_label)
        self.assertIsInstance(self.app_ui.story_text_area, tk.Text, "story_text_area is not a tk.Text.")
        self.assertEqual(self.app_ui.story_text_area.cget('state'), tk.DISABLED, "story_text_area should be disabled initially.")
        self.assertEqual(self.app_ui.story_text_area.cget('wrap'), tk.WORD, "story_text_area wrap mode is not tk.WORD.")

        # Input Entry and Send Button (replaces input_label)
        self.assertIsInstance(self.app_ui.input_entry, tk.Entry, "input_entry is not a tk.Entry.")
        self.assertIsInstance(self.app_ui.send_button, tk.Button, "send_button is not a tk.Button.")
        self.assertEqual(self.app_ui.send_button.cget('text'), "Send", "send_button text is not 'Send'.")

    def test_add_story_text(self):
        """
        Tests the add_story_text method for functionality and state management.
        """
        # Initial state check (optional, but good for confirming setup)
        self.assertEqual(self.app_ui.story_text_area.get("1.0", tk.END).strip(), "", "Story text area should be empty initially.")

        # Add first line
        self.app_ui.add_story_text("Test line 1")
        self.root.update_idletasks() # Ensure UI updates are processed
        self.assertEqual(self.app_ui.story_text_area.get("1.0", tk.END), "Test line 1\n", "First line not added correctly.")
        self.assertEqual(self.app_ui.story_text_area.cget('state'), tk.DISABLED, "Story text area should be disabled after adding text.")

        # Add second line
        self.app_ui.add_story_text("Test line 2")
        self.root.update_idletasks()
        self.assertEqual(self.app_ui.story_text_area.get("1.0", tk.END), "Test line 1\nTest line 2\n", "Second line not appended correctly.")
        self.assertEqual(self.app_ui.story_text_area.cget('state'), tk.DISABLED, "Story text area should be disabled after adding more text.")
        
        # Test scrolling (see method was called) - requires mocking
        # For simplicity, this part is omitted as per typical direct widget testing,
        # but if essential, story_text_area.see could be mocked.

    def test_get_player_input(self):
        """
        Tests the get_player_input method for text retrieval and clearing.
        """
        test_input_string = "Player test input"
        
        # Set text in the input entry
        self.app_ui.input_entry.insert(0, test_input_string)
        self.root.update_idletasks()
        self.assertEqual(self.app_ui.input_entry.get(), test_input_string, "Input entry did not accept text correctly.")

        # Call get_player_input
        retrieved_text = self.app_ui.get_player_input()
        self.root.update_idletasks()

        # Assert retrieved text is correct
        self.assertEqual(retrieved_text, test_input_string, "get_player_input did not return the correct string.")

        # Assert input_entry is now empty
        self.assertEqual(self.app_ui.input_entry.get(), "", "input_entry was not cleared after get_player_input.")


if __name__ == '__main__':
    unittest.main()

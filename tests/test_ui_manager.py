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

    def test_labels_creation_and_text(self):
        """
        Tests if the temporary labels in each frame are created correctly
        and have the specified text and properties.
        """
        # Stats Label
        self.assertIsInstance(self.app_ui.stats_label, tk.Label, "stats_label is not a tk.Label.")
        self.assertEqual(self.app_ui.stats_label.cget('text'), 'Stats Go Here', "stats_label text is incorrect.")

        # Story Label
        self.assertIsInstance(self.app_ui.story_label, tk.Label, "story_label is not a tk.Label.")
        self.assertEqual(self.app_ui.story_label.cget('text'), 'Story Goes Here', "story_label text is incorrect.")
        self.assertEqual(self.app_ui.story_label.cget('fg'), 'white', "story_label foreground color is incorrect.")
        # Background color is inherited from the frame, can also check self.app_ui.story_label.cget('bg') == 'black'

        # Input Label
        self.assertIsInstance(self.app_ui.input_label, tk.Label, "input_label is not a tk.Label.")
        self.assertEqual(self.app_ui.input_label.cget('text'), 'Input Goes Here', "input_label text is incorrect.")

if __name__ == '__main__':
    unittest.main()

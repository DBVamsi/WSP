import unittest
import sys
import os

# Add the parent directory to the Python path to allow importing from game_engine
# This assumes the tests directory is one level down from the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_engine.character_manager import Player

class TestPlayer(unittest.TestCase):
    """
    Test suite for the Player class from character_manager.
    """

    def test_player_creation(self):
        """
        Tests if a Player object is initialized with the correct attributes and types.
        """
        player_id = 1
        name = "Test Hero"
        hp = 80
        max_hp = 100
        mp = 40
        max_mp = 50

        player = Player(player_id, name, hp, max_hp, mp, max_mp)

        # Assert that attributes are set correctly
        self.assertEqual(player.player_id, player_id, "player_id does not match.")
        self.assertEqual(player.name, name, "name does not match.")
        self.assertEqual(player.hp, hp, "hp does not match.")
        self.assertEqual(player.max_hp, max_hp, "max_hp does not match.")
        self.assertEqual(player.mp, mp, "mp does not match.")
        self.assertEqual(player.max_mp, max_mp, "max_mp does not match.")

        # Assert that attributes have the correct types
        self.assertIsInstance(player.player_id, int, "player_id is not an integer.")
        self.assertIsInstance(player.name, str, "name is not a string.")
        self.assertIsInstance(player.hp, int, "hp is not an integer.")
        self.assertIsInstance(player.max_hp, int, "max_hp is not an integer.")
        self.assertIsInstance(player.mp, int, "mp is not an integer.")
        self.assertIsInstance(player.max_mp, int, "max_mp is not an integer.")

        # Assert new attributes
        self.assertEqual(player.current_location, 'Battlefield - Edge of the Kurukshetra',
                         "current_location does not match default value.")
        self.assertIsInstance(player.current_location, str, "current_location is not a string.")

        self.assertEqual(player.story_flags, {}, "story_flags is not an empty dict by default.")
        self.assertIsInstance(player.story_flags, dict, "story_flags is not a dictionary.")


    def test_player_representation(self):
        """
        Tests the __repr__ method of the Player class.
        """
        player = Player(player_id=2, name="Mage", hp=60, max_hp=60, mp=120, max_mp=120)
        # Expected representation now includes location and flags
        expected_repr = ("Player(player_id=2, name='Mage', hp=60/60, mp=120/120, "
                         "location='Battlefield - Edge of the Kurukshetra', flags={})")
        self.assertEqual(repr(player), expected_repr, "__repr__ output is not as expected.")

if __name__ == '__main__':
    unittest.main()

import unittest
import sqlite3
import os
import sys

# Add the parent directory to the Python path to allow importing from game_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_engine.persistence_service import setup_database, save_player, load_player
from game_engine.character_manager import Player # Import Player class
import json # Import json

class TestPersistenceService(unittest.TestCase):
    """
    Test suite for the persistence_service module.
    """
    test_db_path = 'test_rpg_save.db'
    data_dir = 'data_test' # Using a separate directory for test databases

    @classmethod
    def setUpClass(cls):
        """
        Set up resources for the entire test class.
        Ensures the test data directory exists.
        """
        if not os.path.exists(cls.data_dir):
            os.makedirs(cls.data_dir)
        cls.test_db_path = os.path.join(cls.data_dir, 'test_rpg_save.db')


    def setUp(self):
        """
        Set up resources before each test.
        Deletes any existing test database file to ensure a clean state.
        Calls setup_database with the test database path.
        """
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        # Call setup_database to create the database and table for each test
        setup_database(self.test_db_path)

        # Player data for testing load_player
        self.player1_data = {
            "player_id": 1, "name": "Test Player 1", "hp": 100, "max_hp": 100,
            "mp": 50, "max_mp": 50, "current_location": "Test Location",
            "story_flags": {"key1": "value1", "visited_town": True}
        }
        player_obj = Player(
            player_id=self.player1_data["player_id"],
            name=self.player1_data["name"],
            hp=self.player1_data["hp"],
            max_hp=self.player1_data["max_hp"],
            mp=self.player1_data["mp"],
            max_mp=self.player1_data["max_mp"]
        )
        player_obj.current_location = self.player1_data["current_location"]
        player_obj.story_flags = self.player1_data["story_flags"]
        save_player(self.test_db_path, player_obj)

    def tearDown(self):
        """
        Clean up resources after each test.
        Deletes the test database file.
        """
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up resources for the entire test class.
        Removes the test data directory if it's empty.
        """
        if os.path.exists(cls.test_db_path): # Ensure file is removed if a test fails before tearDown
             os.remove(cls.test_db_path)
        if os.path.exists(cls.data_dir) and not os.listdir(cls.data_dir):
            os.rmdir(cls.data_dir)
        elif os.path.exists(cls.data_dir): # If other files are there, warn or handle as needed
            print(f"Warning: Test data directory '{cls.data_dir}' not empty after tests.")


    def test_database_creation(self):
        """
        Tests if the setup_database function correctly creates the database file.
        """
        self.assertTrue(os.path.exists(self.test_db_path), "Database file was not created.")

    def test_players_table_creation(self):
        """
        Tests if the 'players' table is created in the database.
        """
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players';")
        result = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(result, "The 'players' table was not found in the database.")
        self.assertEqual(result[0], 'players', "The table found was not named 'players'.")

    def test_players_table_schema(self):
        """
        Tests if the 'players' table has the correct schema (columns, types, PK).
        """
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(players);")
        columns_info = cursor.fetchall()
        conn.close()

        # Expected schema: (cid, name, type, notnull, dflt_value, pk)
        expected_schema = {
            'id': {'type': 'INTEGER', 'notnull': 0, 'pk': 1}, # In SQLite, INTEGER PRIMARY KEY implies NOT NULL
            'name': {'type': 'TEXT', 'notnull': 1, 'pk': 0},
            'hp': {'type': 'INTEGER', 'notnull': 0, 'pk': 0},
            'max_hp': {'type': 'INTEGER', 'notnull': 0, 'pk': 0},
            'mp': {'type': 'INTEGER', 'notnull': 0, 'pk': 0},
            'max_mp': {'type': 'INTEGER', 'notnull': 0, 'pk': 0},
            'current_location': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
            'story_flags': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
        }

        self.assertEqual(len(columns_info), len(expected_schema),
                         f"Expected {len(expected_schema)} columns, but found {len(columns_info)}.")

        for col_info in columns_info:
            col_name = col_info[1]
            col_type = col_info[2]
            col_notnull = col_info[3]
            col_pk = col_info[5]

            self.assertIn(col_name, expected_schema, f"Unexpected column '{col_name}' found.")

            expected_col = expected_schema[col_name]
            self.assertEqual(col_type, expected_col['type'],
                             f"Column '{col_name}' has type '{col_type}', expected '{expected_col['type']}'.")
            # For 'id' which is INTEGER PRIMARY KEY, SQLite's pragma table_info might report notnull as 0,
            # but it's implicitly NOT NULL. The PK flag is more definitive here.
            if col_name != 'id': # 'id' is INTEGER PRIMARY KEY, which implies NOT NULL
                 self.assertEqual(col_notnull, expected_col['notnull'],
                                 f"Column '{col_name}' has notnull flag '{col_notnull}', expected '{expected_col['notnull']}'.")
            self.assertEqual(col_pk, expected_col['pk'],
                             f"Column '{col_name}' has pk flag '{col_pk}', expected '{expected_col['pk']}'.")

    # Helper function to fetch player data
    def get_player_from_db(self, player_id):
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        # Select columns in the order they are defined in the Player object and save_player
        cursor.execute("""
            SELECT id, name, hp, max_hp, mp, max_mp, current_location, story_flags
            FROM players WHERE id = ?
            """, (player_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def test_save_player_insert(self):
        """Tests saving a new player (INSERT case)."""
        test_player = Player(player_id=1, name="HeroArjuna", hp=100, max_hp=100, mp=50, max_mp=50)
        test_player.current_location = "Kurukshetra - Camp"
        test_player.story_flags = {"met_krishna": True, "bow_acquired": False}

        save_player(self.test_db_path, test_player)

        saved_row = self.get_player_from_db(1)
        self.assertIsNotNone(saved_row, "Player data was not inserted.")

        self.assertEqual(saved_row[0], test_player.player_id)
        self.assertEqual(saved_row[1], test_player.name)
        self.assertEqual(saved_row[2], test_player.hp)
        self.assertEqual(saved_row[3], test_player.max_hp)
        self.assertEqual(saved_row[4], test_player.mp)
        self.assertEqual(saved_row[5], test_player.max_mp)
        self.assertEqual(saved_row[6], test_player.current_location)
        self.assertEqual(json.loads(saved_row[7]), test_player.story_flags)

    def test_save_player_update(self):
        """Tests updating an existing player (UPDATE case)."""
        # Initial save (INSERT)
        player_id_to_update = 2
        initial_player = Player(player_id=player_id_to_update, name="Karna", hp=120, max_hp=120, mp=40, max_mp=40)
        initial_player.current_location = "Anga Kingdom"
        initial_player.story_flags = {"cursed": True}
        save_player(self.test_db_path, initial_player)

        # Modify player data
        modified_player = Player(player_id=player_id_to_update, name="Radheya Karna", hp=110, max_hp=125, mp=35, max_mp=45)
        modified_player.current_location = "Kurukshetra - Battlefield"
        modified_player.story_flags = {"cursed": True, "kavacha_kundala_lost": True}

        save_player(self.test_db_path, modified_player)

        updated_row = self.get_player_from_db(player_id_to_update)
        self.assertIsNotNone(updated_row, "Player data was not found after update attempt.")

        self.assertEqual(updated_row[0], modified_player.player_id)
        self.assertEqual(updated_row[1], modified_player.name) # Updated name
        self.assertEqual(updated_row[2], modified_player.hp) # Updated hp
        self.assertEqual(updated_row[3], modified_player.max_hp) # Updated max_hp
        self.assertEqual(updated_row[4], modified_player.mp) # Updated mp
        self.assertEqual(updated_row[5], modified_player.max_mp) # Updated max_mp
        self.assertEqual(updated_row[6], modified_player.current_location) # Updated location
        self.assertEqual(json.loads(updated_row[7]), modified_player.story_flags) # Updated flags

    def test_load_player_exists(self):
        """Tests loading an existing player from the database."""
        loaded_player = load_player(self.test_db_path, 1)
        self.assertIsNotNone(loaded_player, "Failed to load player with ID 1.")

        self.assertEqual(loaded_player.player_id, self.player1_data["player_id"])
        self.assertEqual(loaded_player.name, self.player1_data["name"])
        self.assertEqual(loaded_player.hp, self.player1_data["hp"])
        self.assertEqual(loaded_player.max_hp, self.player1_data["max_hp"])
        self.assertEqual(loaded_player.mp, self.player1_data["mp"])
        self.assertEqual(loaded_player.max_mp, self.player1_data["max_mp"])
        self.assertEqual(loaded_player.current_location, self.player1_data["current_location"])
        self.assertEqual(loaded_player.story_flags, self.player1_data["story_flags"])

    def test_load_player_not_exists(self):
        """Tests loading a player that does not exist in the database."""
        loaded_player = load_player(self.test_db_path, 999)
        self.assertIsNone(loaded_player, "Loaded a player with ID 999, but it should not exist.")

if __name__ == '__main__':
    unittest.main()

import unittest
import sqlite3
import os
import sys

# Add the parent directory to the Python path to allow importing from game_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_engine.persistence_service import setup_database

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

if __name__ == '__main__':
    unittest.main()

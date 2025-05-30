import sqlite3
import json
import os # Already used in __main__, good to have at top if needed elsewhere
import sys # For path manipulation if character_manager is in a different relative path

# Adjust path to import Player class, assuming character_manager.py is in the same directory
# If this file is run directly, this might need adjustment or character_manager.py
# needs to be in PYTHONPATH. For project structure, this should be okay.
# A more robust way for direct execution might involve adding parent dir if files are in subdirs.
try:
    from game_engine.character_manager import Player
except ImportError:
    # This block is to allow the script to run directly for its own testing
    # if game_engine is not in the Python path (e.g. when running from the directory itself)
    # For the actual application run via main.py, this shouldn't be an issue.
    if __name__ == '__main__': # Only adjust path if running this file directly
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from game_engine.character_manager import Player
    else:
        raise # Re-raise if not running directly, means path issue in project context


def setup_database(db_path='data/rpg_save.db'):
    """
    Connects to the SQLite database and creates the 'players' table if it doesn't exist.

    Args:
        db_path (str, optional): The path to the database file.
                                 Defaults to 'data/rpg_save.db'.
    """
    conn = None  # Initialize conn to None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create players table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                hp INTEGER,
                max_hp INTEGER,
                mp INTEGER,
                max_mp INTEGER,
                current_location TEXT,
                story_flags TEXT
            )
        ''')

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Example usage:
    # This will create the database and table in the default location 'data/rpg_save.db'
    # You might need to create the 'data' directory first if it doesn't exist.
    import os
    if not os.path.exists('data'):
        os.makedirs('data')
    setup_database()
    print("Database setup complete. Check for 'data/rpg_save.db'")

    # Example with a different database path:
    # setup_database('custom_db.db')
    # print("Custom database setup complete. Check for 'custom_db.db'")


def save_player(db_path: str, player_obj: Player):
    """
    Saves the player's current state to the database.
    This function will handle both inserting a new player and updating an existing one.
    (Currently a skeleton with placeholder logic)

    Args:
        db_path (str): The path to the SQLite database file.
        player_obj (Player): The Player object to save.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Serialize story_flags
        story_flags_json = json.dumps(player_obj.story_flags)

        # Placeholder for UPDATE and INSERT logic
        # This will be expanded to use player_obj.player_id to check existence,
        # then either UPDATE the existing record or INSERT a new one.

        # Define the SQL UPDATE query
        update_sql = """
        UPDATE players
        SET name = ?, hp = ?, max_hp = ?, mp = ?, max_mp = ?, current_location = ?, story_flags = ?
        WHERE id = ?
        """

        # Create a tuple of values corresponding to the placeholders in the query
        values = (
            player_obj.name,
            player_obj.hp,
            player_obj.max_hp,
            player_obj.mp,
            player_obj.max_mp,
            player_obj.current_location,
            story_flags_json,
            player_obj.player_id
        )

        # Execute the query
        cursor.execute(update_sql, values)

        if cursor.rowcount == 0:
            # Player with this ID doesn't exist, so INSERT
            insert_sql = """
            INSERT INTO players (id, name, hp, max_hp, mp, max_mp, current_location, story_flags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            insert_values = (
                player_obj.player_id,
                player_obj.name,
                player_obj.hp,
                player_obj.max_hp,
                player_obj.mp,
                player_obj.max_mp,
                player_obj.current_location,
                story_flags_json
            )
            cursor.execute(insert_sql, insert_values)
            print(f"Player {player_obj.player_id} inserted.") # Optional: for logging/debug
        else:
            print(f"Player {player_obj.player_id} updated.") # Optional: for logging/debug


        conn.commit()
        # print(f"Player {player_obj.player_id} data changes committed.")

    except sqlite3.Error as e:
        print(f"Database error in save_player for player {player_obj.player_id if player_obj else 'Unknown'}: {e}")
        # Consider how to handle partial saves or rollbacks if needed
    except Exception as e:
        # Catch other potential errors, e.g., from json.dumps or attribute access
        print(f"An unexpected error occurred in save_player: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # ... (existing __main__ block) ...

    # Example for save_player (add this to the existing __main__ if you want to test it)
    print("\n--- Testing save_player (skeleton) ---")
    # Create a dummy Player object for testing
    # Ensure this matches the Player class definition in character_manager.py
    # For this to run, Player class must be importable
    if 'Player' in globals(): # Check if Player class was successfully imported
        test_player = Player(player_id=1, name="TestHero", hp=90, max_hp=110, mp=40, max_mp=60)
        test_player.current_location = "Starting Village"
        test_player.story_flags = {"quest_started": True, "met_npc_rava": False}

        # Use the default db_path from setup_database or specify one
        db_to_save = 'data/rpg_save.db'
        if not os.path.exists(os.path.dirname(db_to_save)):
             os.makedirs(os.path.dirname(db_to_save))
        setup_database(db_to_save) # Ensure table exists

        save_player(db_path=db_to_save, player_obj=test_player)
        print("save_player test completed.")
    else:
        print("Player class not available, skipping save_player test in __main__.")

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
    from .common_types import AdventureLog # Added import
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
                story_flags TEXT,
                inventory TEXT
            )
        ''')
        conn.commit() # Commit table creation before altering

        # Add adventure_log column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE players ADD COLUMN adventure_log TEXT;")
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                # Column already exists, which is fine
                pass
            else:
                # Another OperationalError, raise it
                raise
    except sqlite3.Error as e:
        print(f"Database error in setup_database: {e}")
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

        # Serialize story_flags, inventory, and adventure_log
        story_flags_json = json.dumps(player_obj.story_flags)
        inventory_json = json.dumps(player_obj.inventory if hasattr(player_obj, 'inventory') else [])
        adventure_log_json = None
        if hasattr(player_obj, 'adventure_log') and player_obj.adventure_log:
            try:
                adventure_log_json = player_obj.adventure_log.model_dump_json()
            except AttributeError: # Fallback for Pydantic v1
                adventure_log_json = player_obj.adventure_log.json()


        # Define the SQL UPDATE query
        update_sql = """
        UPDATE players
        SET name = ?, hp = ?, max_hp = ?, mp = ?, max_mp = ?, current_location = ?, story_flags = ?, inventory = ?, adventure_log = ?
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
            inventory_json,
            adventure_log_json, # Added adventure_log_json
            player_obj.player_id
        )

        # Execute the query
        cursor.execute(update_sql, values)

        if cursor.rowcount == 0:
            # Player with this ID doesn't exist, so INSERT
            insert_sql = """
            INSERT INTO players (id, name, hp, max_hp, mp, max_mp, current_location, story_flags, inventory, adventure_log)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            insert_values = (
                player_obj.player_id,
                player_obj.name,
                player_obj.hp,
                player_obj.max_hp,
                player_obj.mp,
                player_obj.max_mp,
                player_obj.current_location,
                story_flags_json,
                inventory_json,
                adventure_log_json # Added adventure_log_json
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


def load_player(db_path: str, player_id: int):
    """
    Loads a player's state from the database.

    Args:
        db_path (str): The path to the SQLite database file.
        player_id (int): The ID of the player to load.

    Returns:
        Player: The loaded Player object, or None if not found or an error occurs.
    """
    conn = None
    player = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name, hp, max_hp, mp, max_mp, current_location, story_flags, inventory, adventure_log FROM players WHERE id = ?", # Added adventure_log
            (player_id,)
        )
        row = cursor.fetchone()

        if row:
            db_id, name, hp, max_hp, mp, max_mp, current_location, story_flags_json, inventory_json, adventure_log_json = row # Added adventure_log_json

            story_flags = json.loads(story_flags_json)

            inventory = [] # Default to empty list
            if inventory_json: # Check if inventory_json is not None or empty string
                try:
                    inventory = json.loads(inventory_json)
                except json.JSONDecodeError:
                    print(f"Error decoding inventory JSON for player_id {player_id}: {inventory_json}")
                    # Keep inventory as empty list or handle error as appropriate

            # Assuming Player.__init__ might not take inventory directly, or we want to ensure it's handled post-init
            # Assuming Player.__init__ might not take inventory directly, or we want to ensure it's handled post-init
            player = Player(player_id=db_id, name=name, hp=hp, max_hp=max_hp, mp=mp, max_mp=max_mp) # AdventureLog will be default
            player.current_location = current_location
            player.story_flags = story_flags
            player.inventory = inventory

            if adventure_log_json:
                try:
                    player.adventure_log = AdventureLog.model_validate_json(adventure_log_json)
                except AttributeError: # Fallback for Pydantic v1
                    player.adventure_log = AdventureLog.parse_raw(adventure_log_json)
                except Exception as e: # Catch potential Pydantic validation errors
                    print(f"Error decoding AdventureLog JSON for player_id {player_id}: {e}")
                    player.adventure_log = AdventureLog() # Default to empty log on error
            else:
                player.adventure_log = AdventureLog() # Initialize new log if none in DB

    except sqlite3.Error as e:
        print(f"Database error in load_player for player_id {player_id}: {e}")
    finally:
        if conn:
            conn.close()
    return player

if __name__ == '__main__':
    # ... (existing __main__ block) ...

    # Example for save_player (add this to the existing __main__ if you want to test it)
    print("\n--- Testing save_player (skeleton) ---")
    # Create a dummy Player object for testing
    # Ensure this matches the Player class definition in character_manager.py
    # For this to run, Player class must be importable
    if 'Player' in globals() and 'AdventureLog' in globals(): # Check if Player and AdventureLog classes were successfully imported
        print("\n--- Testing save_player and load_player with AdventureLog ---")
        db_path_main = 'data/rpg_save_main_test.db' # Use a distinct DB for this test
        if not os.path.exists(os.path.dirname(db_path_main)):
            os.makedirs(os.path.dirname(db_path_main))
        setup_database(db_path_main) # Ensure table exists with adventure_log column

        # Create a Player object
        player_to_save = Player(player_id=101, name="LogHero", hp=100, max_hp=100, mp=50, max_mp=50)
        player_to_save.current_location = "Library of Scribes"
        player_to_save.inventory = ["Ancient Tome", "Quill"]
        # Add an entry to the adventure log
        if player_to_save.adventure_log: # Should exist by default
            from game_engine.common_types import AdventureLogEntry # Import for test entry
            log_entry = AdventureLogEntry(type="test_event", content="Player created for persistence test.", turn_number=1)
            player_to_save.adventure_log.entries.append(log_entry)

        # Save the player
        save_player(db_path=db_path_main, player_obj=player_to_save)
        print(f"Player '{player_to_save.name}' saved with {len(player_to_save.adventure_log.entries)} log entries.")

        # Load the player
        loaded_player = load_player(db_path=db_path_main, player_id=player_to_save.player_id)

        if loaded_player:
            print(f"Player '{loaded_player.name}' loaded.")
            print(f"  HP: {loaded_player.hp}/{loaded_player.max_hp}")
            print(f"  Location: {loaded_player.current_location}")
            print(f"  Inventory: {loaded_player.inventory}")
            if loaded_player.adventure_log:
                print(f"  Adventure Log Entries: {len(loaded_player.adventure_log.entries)}")
                if loaded_player.adventure_log.entries:
                    print(f"    Last entry: {loaded_player.adventure_log.entries[-1].type} - '{loaded_player.adventure_log.entries[-1].content}' at turn {loaded_player.adventure_log.entries[-1].turn_number}")
            else:
                print("  Adventure Log: Not found or empty.")
        else:
            print(f"Failed to load player {player_to_save.player_id}.")

        # Clean up the test database file
        # os.remove(db_path_main)
        # print(f"Cleaned up test database: {db_path_main}")

    else:
        print("Player or AdventureLog class not available, skipping save/load test in __main__.")

import sqlite3

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
                max_mp INTEGER
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

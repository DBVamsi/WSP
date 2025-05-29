from game_engine.persistence_service import setup_database
import os

def main():
    """
    Main function to run the RPG game.
    """
    # Ensure the 'data' directory exists before setting up the database
    data_dir = 'data'
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
            print(f"Directory '{data_dir}' created.")
        except OSError as e:
            print(f"Error creating directory '{data_dir}': {e}")
            # Optionally, exit or raise the error if the directory is critical
            return 

    print("Setting up the database...")
    setup_database()
    print("Database setup complete.")
    
    # Future game logic will go here
    print("Game starting...")
    # For now, let's just print a message
    print("Welcome to the RPG!")

if __name__ == '__main__':
    main()

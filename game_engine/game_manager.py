import tkinter as tk
import os
import sys

# Adjust path to import from parent directory (root) and sibling (ui)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.ui_manager import GameUI
from game_engine.persistence_service import setup_database

class GameManager:
    """
    Manages the overall game state, UI, and core game logic.
    """
    def __init__(self):
        """
        Initializes the GameManager, sets up the database, and prepares the UI.
        """
        # Ensure the 'data' directory exists before setting up the database
        # This is important because persistence_service might try to create a DB there.
        data_dir = 'data'
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir)
                print(f"Directory '{data_dir}' created by GameManager.")
            except OSError as e:
                print(f"Error creating directory '{data_dir}' in GameManager: {e}")
                # Depending on the game's needs, might raise error or exit
                return

        print("GameManager: Setting up database...")
        setup_database() # Call to set up the database
        print("GameManager: Database setup complete.")

        print("GameManager: Initializing UI...")
        self.root = tk.Tk()
        self.ui = GameUI(self.root) # Create GameUI instance
        print("GameManager: UI initialized.")

    def start_game(self):
        """
        Starts the main game UI loop.
        """
        if hasattr(self, 'ui') and self.ui:
            print("GameManager: Starting UI...")
            self.ui.start_ui()
        else:
            print("GameManager: Error - UI not initialized. Cannot start game.")

if __name__ == '__main__':
    # This block is for testing the GameManager independently.
    print("Initializing GameManager for testing...")
    game_manager = GameManager()
    print("GameManager initialized.")
    
    # To actually see the UI during testing, you would call:
    # print("Starting game UI for testing...")
    # game_manager.start_game() 
    # print("Game UI finished or closed.")
    
    # For now, just confirm it ran without starting the mainloop,
    # as per the task focusing on __init__
    if hasattr(game_manager, 'root') and game_manager.root:
        print("GameManager root window created.")
        game_manager.root.destroy() # Clean up the root window if not starting mainloop
    else:
        print("GameManager root window not created (possibly due to earlier error).")

from game_engine.game_manager import GameManager
# import os # No longer needed here as GameManager handles data directory
# import tkinter as tk # No longer needed here
# from ui.ui_manager import GameUI # No longer needed here
# from game_engine.persistence_service import setup_database # No longer needed here

def main():
    """
    Main function to initialize and run the RPG game using GameManager.
    """
    print("Main: Initializing GameManager...")
    game_manager = GameManager()
    print("Main: GameManager initialized.")
    
    print("Main: Starting game...")
    game_manager.start_game() # This will initialize DB, UI, and start the UI loop
    
    print("Main: Game has finished or UI was closed.")

if __name__ == '__main__':
    main()

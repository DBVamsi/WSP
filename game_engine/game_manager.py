import tkinter as tk
import os
import sys

# Adjust path to import from parent directory (root) and sibling (ui)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.ui_manager import GameUI
from game_engine.persistence_service import setup_database, save_player, load_player
from game_engine.input_parser import parse_input
from game_engine.ai_dm_interface import AIDungeonMaster
from game_engine.character_manager import Player

DB_PATH = 'data/rpg_save.db'

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

        # Ensure the 'data' directory exists - This part can remain early.
        # The actual DB setup call will be moved as per instructions.

        print("GameManager: Initializing UI...")
        self.root = tk.Tk()
        self.ui = GameUI(self.root, self) # Pass GameManager instance to GameUI
        print("GameManager: UI initialized.")

        # Database setup and Player loading, as per subtask instructions
        print("GameManager: Setting up database (after UI init)...")
        setup_database(DB_PATH)
        print("GameManager: Database setup complete.")

        print("GameManager: Loading player...")
        self.player = load_player(DB_PATH, player_id=1)
        if self.player is None:
            print("GameManager: No player found, creating new default player.")
            self.player = Player(player_id=1, name='Veera', hp=100, max_hp=100, mp=50, max_mp=50)
            self.player.current_location = 'Kurukshetra - Battlefield Edge'
            self.player.story_flags = {'war_just_started': True}
            self.player.inventory = ["a simple dagger", "a healing herb"] # Default inventory
            save_player(DB_PATH, self.player)
            print(f"GameManager: New player '{self.player.name}' created and saved with default inventory.")
            print(f"GameManager: New player '{self.player.name}' created and saved with default inventory.")
        else:
            print(f"GameManager: Player '{self.player.name}' loaded successfully.")
            # Optional: Log loaded inventory
            if hasattr(self.player, 'inventory'):
                print(f"GameManager: Player '{self.player.name}' inventory: {self.player.inventory}")


        print("GameManager: Initializing AI Dungeon Master...")
        api_key_from_input = input('Please enter your Google AI API Key: ')
        self.ai_dm = AIDungeonMaster(api_key=api_key_from_input)
        print("GameManager: AI Dungeon Master initialized.")


    def start_game(self):
        """
        Starts the main game UI loop.
        """
        if hasattr(self, 'ui') and self.ui and hasattr(self, 'ai_dm'):
            print("GameManager: Getting initial scene from AI DM...")
            initial_description = self.ai_dm.get_initial_scene_description()
            print("GameManager: Initial scene received. Displaying...")
            self.ui.add_story_text(initial_description)
            print("GameManager: Initial scene processed.")

            print("GameManager: Starting UI...")
            self.ui.start_ui()
        elif not hasattr(self, 'ui') or not self.ui:
            print("GameManager: Error - UI not initialized. Cannot start game.")
        else: # ai_dm is missing
            print("GameManager: Error - AI DM not initialized. Cannot start game.")


    def process_player_command(self):
        """
        Retrieves player input from the UI, processes it, and displays feedback.
        """
        command_string = self.ui.get_player_input()
        stripped_command = command_string.strip() # Get a stripped version once

        if stripped_command: # Check if the stripped command is not empty
            self.ui.add_story_text(f'You typed: {stripped_command}')

            # Call parse_input (already imported)
            parsed_command = parse_input(stripped_command)

            # Placeholder for actual command processing logic
            # For now, just acknowledge the parsed command (which is same as stripped_command)
            # self.ui.add_story_text(f'Parsed as: {parsed_command}') # Optional debug line

            # Get AI response to the player's command
            # Pass the player object and the parsed command to the AI DM
            if hasattr(self, 'player') and self.player is not None:
                ai_response = self.ai_dm.get_ai_response(player_object=self.player, player_action=parsed_command)
                self.ui.add_story_text(ai_response)
            else:
                # This case should ideally not happen if player is always loaded/created in __init__
                self.ui.add_story_text("Error: Player data is not available. Cannot process command.")
        # else:
            # Optionally, handle empty input, e.g., self.ui.add_story_text("Please enter a command.")
            # For now, empty input is silently ignored as per the conditional check.

    def quit_game(self):
        """
        Saves the player's state, prints an exit message, and closes the Tkinter window.
        """
        if hasattr(self, 'player') and self.player is not None:
            print(f"GameManager: Saving player '{self.player.name}' before quitting...")
            save_player(DB_PATH, self.player)
            print("Game saved. Exiting...")
        else:
            print("GameManager: No player data to save. Exiting...")

        if hasattr(self, 'root') and self.root:
            self.root.destroy()
        else:
            print("GameManager: No root window to destroy.")


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

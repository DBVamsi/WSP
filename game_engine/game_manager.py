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
from .common_types import GameStateUpdates # Import for type hinting and usage

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
        else:
            print(f"GameManager: Player '{self.player.name}' loaded successfully.")
            # Optional: Log loaded inventory
            if hasattr(self.player, 'inventory'):
                print(f"GameManager: Player '{self.player.name}' inventory: {self.player.inventory}")

        # Update the UI with the loaded/created player's details
        if self.player and hasattr(self.ui, 'update_player_display'): # Ensure player and method exist
            self.ui.update_player_display(self.player)


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

            # Update player display after initial scene
            if self.player and hasattr(self.ui, 'update_player_display'):
                self.ui.update_player_display(self.player)

            # Display player's skills at the start of the game
            if self.player and hasattr(self.player, 'skills') and self.player.skills:
                self.ui.add_story_text(f"Your available skills: {', '.join(self.player.skills)}")
            else:
                self.ui.add_story_text("You currently have no special skills.")


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
        # We'll use stripped_command for the AI and UI message for now
        stripped_command = command_string.strip()

        # Use the new parser
        parsed_result = parse_input(command_string)
        command = parsed_result['command']
        arguments = parsed_result['arguments']

        if command is None:
            self.ui.add_story_text("Please enter a command.")
            return

        # Display the original typed command (can be adjusted later if needed)
        self.ui.add_story_text(f'You typed: {stripped_command}')

        # Future game logic will use 'command' and 'arguments'.
        # For example, a "use" command might check arguments:
        # if command == "use" and arguments:
        #     self.ui.add_story_text(f"You try to use {arguments[0]}.")
        # elif command == "use":
        #     self.ui.add_story_text("Use what?")

        # Current interaction with AI_DM uses the full stripped_command.
        # This can be revisited if AI needs more structured input.
        player_action_for_ai = stripped_command

        if hasattr(self, 'player') and self.player is not None:
            # Pass the original stripped_command as player_action to the AI DM
            # This is because the AI is currently tuned for full sentences.
            # The parsed 'command' and 'arguments' will be used for client-side logic.
            narrative, game_updates = self.ai_dm.get_ai_response(player_object=self.player, player_action=player_action_for_ai)
            self.ui.add_story_text(narrative) # Display the narrative from AI

            # Apply game state updates received from the AI
            if game_updates: # game_updates will be an instance of GameStateUpdates
                # Display skill usage first if a skill was used
                if game_updates.skill_used:
                    self.ui.add_story_text(f"[System: You used {game_updates.skill_used}!]")

                # Apply inventory changes
                if game_updates.inventory_add:
                    for item in game_updates.inventory_add:
                        self.player.inventory.append(item)
                        self.ui.add_story_text(f"[System: '{item}' added to inventory.]")

                if game_updates.inventory_remove:
                    for item in game_updates.inventory_remove:
                        if item in self.player.inventory:
                            self.player.inventory.remove(item)
                            self.ui.add_story_text(f"[System: '{item}' removed from inventory.]")
                        else:
                            self.ui.add_story_text(f"[System: Tried to remove '{item}', but it wasn't in inventory.]")

                # Apply HP changes (after skill message, if any)
                if game_updates.hp_change != 0:
                    self.player.hp += game_updates.hp_change
                    self.player.hp = max(0, min(self.player.hp, self.player.max_hp)) # Clamp HP
                    self.ui.add_story_text(f"[System: HP changed by {game_updates.hp_change}. Current HP: {self.player.hp}/{self.player.max_hp}]")

                # Apply MP changes
                if game_updates.mp_change != 0:
                    self.player.mp += game_updates.mp_change
                    self.player.mp = max(0, min(self.player.mp, self.player.max_mp)) # Clamp MP
                    self.ui.add_story_text(f"[System: MP changed by {game_updates.mp_change}. Current MP: {self.player.mp}/{self.player.max_mp}]")

                # Apply story flag changes
                if game_updates.new_story_flags:
                    self.player.story_flags.update(game_updates.new_story_flags)
                    self.ui.add_story_text(f"[System: Story flags updated: {game_updates.new_story_flags}]")

                # Apply location changes
                if game_updates.new_location and game_updates.new_location != self.player.current_location:
                    self.player.current_location = game_updates.new_location
                    self.ui.add_story_text(f"[System: Location changed to: {self.player.current_location}]")

                # Optional: Log the full state of the player after updates for debugging
                # print(f"Player state after updates: {self.player}")

                # Apply player name change
                if game_updates.player_name and isinstance(game_updates.player_name, str) and game_updates.player_name.strip():
                    if self.player.name != game_updates.player_name:
                        old_name = self.player.name
                        self.player.name = game_updates.player_name.strip()
                        self.ui.add_story_text(f"[System: Player name changed from '{old_name}' to '{self.player.name}'.]")

                # Refresh the UI display with the new player state
                if self.player and hasattr(self.ui, 'update_player_display'):
                    self.ui.update_player_display(self.player)
        else: # This else clause pairs with "if hasattr(self, 'player') and self.player is not None:"
            # This case should ideally not happen if player is always loaded/created in __init__
            self.ui.add_story_text("Error: Player data is not available. Cannot process command.")
        # The outer 'if command is None:' handles empty/whitespace input.
        # No additional 'else' is needed here for that case.

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

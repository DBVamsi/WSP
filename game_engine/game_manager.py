import os
import sys

# Adjust path to import from parent directory (root)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Removed: from ui.ui_manager import GameUI (Tkinter)
# Removed: import tkinter as tk

from game_engine.persistence_service import setup_database, save_player, load_player
from game_engine.input_parser import parse_input
from game_engine.ai_dm_interface import AIDungeonMaster
from game_engine.character_manager import Player
from .common_types import GameStateUpdates # Import for type hinting and usage
# ui.web_ui_manager is imported in main.py and instance is passed

DB_PATH = 'data/rpg_save.db'

class GameManager:
    """
    Manages the overall game state, UI, and core game logic.
    Adapted for WebUIManager using Eel.
    """
    def __init__(self, ui_manager): # ui_manager is now injected
        """
        Initializes the GameManager, sets up the database.
        UI initialization is now handled by main.py with Eel.
        """
        self.ui = ui_manager # Store the passed WebUIManager instance
        self.player: Player | None = None
        self.ai_dm: AIDungeonMaster | None = None

        data_dir = 'data'
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir)
                print(f"Directory '{data_dir}' created by GameManager.")
            except OSError as e:
                print(f"Error creating directory '{data_dir}' in GameManager: {e}")
                return

        print("GameManager: Setting up database...")
        setup_database(DB_PATH)
        print("GameManager: Database setup complete.")

        print("GameManager: Loading player...")
        self.player = load_player(DB_PATH, player_id=1)
        if self.player is None:
            print("GameManager: No player found, creating new default player.")
            self.player = Player(player_id=1, name='Veera', hp=100, max_hp=100, mp=50, max_mp=50)
            self.player.current_location = 'Kurukshetra - Battlefield Edge' # Default location
            self.player.story_flags = {'war_just_started': True}
            self.player.inventory = ["a simple dagger", "a healing herb"]
            # Default skills are set in Player class: ["Meditate", "Power Attack"]
            save_player(DB_PATH, self.player)
            print(f"GameManager: New player '{self.player.name}' created and saved.")
        else:
            print(f"GameManager: Player '{self.player.name}' loaded successfully.")
            if not hasattr(self.player, 'skills') or not self.player.skills:
                 # For players saved before skills were introduced
                print(f"GameManager: Player '{self.player.name}' has no skills, assigning defaults.")
                self.player.skills = ["Meditate", "Power Attack"] # Default skills
                save_player(DB_PATH, self.player) # Save updated player

        # DO NOT update UI (e.g. self.ui.update_player_display(self.player)) here.
        # This will be done in initialize_game_state_and_ui after JS is ready.

        print("GameManager: Initializing AI Dungeon Master...")
        # In a real app, API key might come from a config file or secure input
        # For now, let's keep the input, but acknowledge it's blocking for Eel startup.
        # Consider moving this to after JS ready if it's problematic.
        try:
            api_key_from_input = os.getenv("GOOGLE_API_KEY")
            if not api_key_from_input: # Fallback if env var is not set
                 api_key_from_input = input('Please enter your Google AI API Key (or set GOOGLE_API_KEY env var): ')
            self.ai_dm = AIDungeonMaster(api_key=api_key_from_input)
            print("GameManager: AI Dungeon Master initialized.")
        except Exception as e:
            print(f"GameManager: Error initializing AI DM: {e}")
            if self.ui and hasattr(self.ui, 'add_story_text') and self.ui.is_ready:
                self.ui.add_story_text(f"[System Error: Could not initialize AI. Game may not function. {e}]")
            # Potentially re-raise or handle to prevent game from starting without AI

    def initialize_game_state_and_ui(self):
        """
        Called once JavaScript is ready. Sends initial game state to UI.
        """
        print("GameManager: JS is ready, initializing game state and UI.")
        if not self.player:
            self.ui.add_story_text("[System Error: Player not loaded. Cannot start game.]")
            return
        if not self.ai_dm:
            self.ui.add_story_text("[System Error: AI Dungeon Master not initialized. Cannot start game.]")
            return

        initial_description = self.ai_dm.get_initial_scene_description()
        self.ui.add_story_text(initial_description)
        self.ui.update_player_display(self.player)

        if self.player.skills:
            self.ui.add_story_text(f"Your available skills: {', '.join(self.player.skills)}")
        else:
            self.ui.add_story_text("You currently have no special skills.")
        self.ui.add_story_text("Type your commands below and press Enter or click Send.")


    def start_game(self):
        """
        Eel handles the UI loop. This method is now mostly a placeholder.
        The actual UI start is eel.start() in main.py.
        """
        print("GameManager: start_game() called. UI is JS-driven by Eel.")
        # If there's any non-UI setup that needs to happen before game interaction starts,
        # but after JS is ready, it could go here. For now, covered by initialize_game_state_and_ui.

    def process_player_command_from_js(self, command_string: str):
        """
        Processes player command received from JS, updates game state, and UI.
        """
        if not self.player or not self.ai_dm:
            self.ui.add_story_text("[System Error: Game not fully initialized. Cannot process command.]")
            return

        # command_string is already provided by JS
        stripped_command = command_string.strip()

        parsed_result = parse_input(command_string) # Normalizes and splits
        command_verb = parsed_result['command']
        # arguments = parsed_result['arguments'] # Available if needed for client-side logic

        if command_verb is None:
            self.ui.add_story_text("Please enter a command.")
            return

        self.ui.add_story_text(f"> {stripped_command}") # Display player's command

        # AI interaction using the full stripped_command
        player_action_for_ai = stripped_command
        narrative, game_updates = self.ai_dm.get_ai_response(
            player_object=self.player,
            player_action=player_action_for_ai
        )
        self.ui.add_story_text(narrative)

        if game_updates:
            if game_updates.skill_used:
                self.ui.add_story_text(f"[System: You used {game_updates.skill_used}!]")

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

            if game_updates.hp_change != 0:
                self.player.hp += game_updates.hp_change
                self.player.hp = max(0, min(self.player.hp, self.player.max_hp))
                # self.ui.add_story_text(f"[System: HP changed by {game_updates.hp_change}. Current HP: {self.player.hp}/{self.player.max_hp}]") # Handled by update_player_display
            if game_updates.mp_change != 0:
                self.player.mp += game_updates.mp_change
                self.player.mp = max(0, min(self.player.mp, self.player.max_mp))
                # self.ui.add_story_text(f"[System: MP changed by {game_updates.mp_change}. Current MP: {self.player.mp}/{self.player.max_mp}]") # Handled by update_player_display

            if game_updates.new_story_flags:
                self.player.story_flags.update(game_updates.new_story_flags)
                self.ui.add_story_text(f"[System: Story flags updated: {game_updates.new_story_flags}]")
            if game_updates.new_location and game_updates.new_location != self.player.current_location:
                self.player.current_location = game_updates.new_location
                self.ui.add_story_text(f"[System: Location changed to: {self.player.current_location}]")
            if game_updates.player_name and isinstance(game_updates.player_name, str) and game_updates.player_name.strip():
                if self.player.name != game_updates.player_name:
                    old_name = self.player.name
                    self.player.name = game_updates.player_name.strip()
                    self.ui.add_story_text(f"[System: Player name changed from '{old_name}' to '{self.player.name}'.]")

            # Refresh the entire player display panel after all changes
            self.ui.update_player_display(self.player)

            # Save player state after updates
            save_player(DB_PATH, self.player)


    def quit_game(self):
        """
        Saves the player's state. UI closing is handled by Eel or Python exit.
        """
        if hasattr(self, 'player') and self.player is not None:
            print(f"GameManager: Saving player '{self.player.name}' before quitting...")
            save_player(DB_PATH, self.player)
            print("Game saved.")
        else:
            print("GameManager: No player data to save.")

        print("GameManager: Exiting application via sys.exit().")
        sys.exit(0) # Request a clean exit


# The __main__ block for direct testing of GameManager is no longer suitable
# with the Eel UI dependency. Testing would need to be refactored,
# possibly by mocking the WebUIManager.
# if __name__ == '__main__':
#     print("GameManager direct execution is not supported with WebUIManager.")
#     # Example:
#     # class MockWebUI:
#     #     def __init__(self): self.is_ready = True
#     #     def set_ready(self): pass
#     #     def add_story_text(self, t): print(f"UI-Story: {t}")
#     #     def update_player_display(self, p): print(f"UI-Stats: HP {p.hp}/{p.max_hp} MP {p.mp}/{p.max_mp} Loc: {p.current_location} Inv: {p.inventory} Skills: {p.skills}")
#     # mock_ui = MockWebUI()
#     # game_manager = GameManager(ui_manager=mock_ui)
#     # game_manager.initialize_game_state_and_ui()
#     # game_manager.process_player_command_from_js("look around")
#     # game_manager.quit_game()

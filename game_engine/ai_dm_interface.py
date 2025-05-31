import google.generativeai as genai
import os # For potentially loading API key from environment
import json # For parsing AI response
from game_engine.character_manager import Player # For type hinting
from .common_types import GameStateUpdates # For structuring game state updates

class AIDungeonMaster:
    """
    Manages interactions with the AI Dungeon Master (DM) using Google's Generative AI.
    """
    def __init__(self, api_key: str = None):
        """
        Initializes the AI Dungeon Master.

        Args:
            api_key (str, optional): The API key for Google's Generative AI.
                                     If None, it will attempt to load from the
                                     GOOGLE_API_KEY environment variable.

        Raises:
            ValueError: If the API key is not provided and not found in the environment.
        """
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("API key not provided and GOOGLE_API_KEY environment variable not set.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        # Further model configuration (e.g., safety settings, generation config) can be done here
        # self.model.safety_settings = ...
        # self.model.generation_config = ...

    def get_initial_scene_description(self) -> str:
        """
        Generates and returns the initial scene description for the player's adventure.

        Returns:
            str: A string containing the scene description, or an error message if generation fails.
        """
        prompt_string = (
            'You are a Dungeon Master for a text-based RPG set in a world inspired by Indian Mythology, '
            'focusing on a great war between Devas and Asuras where the player is caught in the middle. '
            'Describe the very first intriguing scene the player encounters as they begin their adventure. '
            'Keep it to 3-4 concise sentences.'
        )
        try:
            response = self.model.generate_content(prompt_string)
            # Consider adding more robust error checking for response if needed,
            # e.g., checking response.prompt_feedback for block reasons.
            return response.text
        except Exception as e:
            print(f'Error contacting AI DM for initial scene: {e}')
            return 'Error: The mists of creation obscure your vision... Please check your connection or API key.'

    def get_ai_response(self, player_object: Player, player_action: str) -> tuple[str, GameStateUpdates]:
        """
        Generates and returns the AI DM's response, including narrative and game state updates.

        Args:
            player_object (Player): The player character object.
            player_action (str): The action taken by the player.

        Returns:
            tuple[str, GameStateUpdates]: A tuple containing the narrative string and
                                          a GameStateUpdates object.
        """
        prompt_string = f"""You are the Dungeon Master for a text-based RPG inspired by Indian Mythology, focusing on a great war between Devas and Asuras.
The player is {player_object.name}.
Player's current status: HP: {player_object.hp}/{player_object.max_hp}, MP: {player_object.mp}/{player_object.max_mp}.
Player's current location: {player_object.current_location}.
Player's inventory: {str(player_object.inventory if hasattr(player_object, 'inventory') else [])}.
Key story events/flags known so far: {str(player_object.story_flags)}.

The player says: "{player_action}"

Your response MUST be a valid JSON object with two top-level keys: "narrative" and "game_state_updates".
1.  `"narrative"`: String (3-5 sentences) describing what happens next. Maintain theme and consider player's situation.
2.  `"game_state_updates"`: JSON object for player/world changes. Omit keys or use default values if no change for an aspect.
    Fields for `"game_state_updates"` (use defaults if no change):
    -   `"inventory_add"`: list[str] - Items to add. Default: [].
    -   `"inventory_remove"`: list[str] - Items to remove. Default: [].
    -   `"hp_change"`: int - Player HP change. Default: 0.
    -   `"mp_change"`: int - Player MP change. Default: 0.
    -   `"new_story_flags"`: object - Story flags to set/update. Default: {{}}.
    -   `"new_location"`: str | null - Player's new location. Default: null.
    -   `"player_name"`: str | null - Player's new name. Default: null.

Example 1 (Comprehensive update):
```json
{{
    "narrative": "You feel weaker after the Asura's curse and notice your favorite dagger is gone, but you find a healing herb.",
    "game_state_updates": {{
        "inventory_add": ["healing herb"],
        "inventory_remove": ["favorite dagger"],
        "hp_change": -10,
        "mp_change": -5,
        "new_story_flags": {{"cursed": true}},
        "player_name": "Weakened Player"
    }}
}}
```
Example 2 (Narrative only, no state changes):
```json
{{
    "narrative": "You look around but find nothing of interest, and nothing about you changes.",
    "game_state_updates": {{}}
}}
```
Ensure your output is a single, valid JSON object. Only include changed fields in `game_state_updates`.
"""
        response_text = ""
        try:
            # Log the prompt that will be sent
            print(f"--- PROMPT SENT TO AI (expecting JSON response) ---\n{prompt_string}\n-------------------------")

            response = self.model.generate_content(prompt_string)
            response_text = response.text
            original_response_text_for_debugging = response_text # Keep a copy for debug log

            # Clean up potential markdown fences around the JSON
            if response_text.startswith("```json\n") and response_text.endswith("\n```"):
                response_text = response_text[len("```json\n"):-len("\n```")]
            elif response_text.startswith("```") and response_text.endswith("```"):
                lines = response_text.splitlines()
                if len(lines) > 2 and lines[0] == "```" and lines[-1] == "```":
                    response_text = "\n".join(lines[1:-1])
                elif lines[0].startswith("```json") and lines[-1] == "```": # Single line case
                     response_text = lines[0][len("```json"):].strip()
                     if response_text.endswith("```"):
                         response_text = response_text[:-len("```")].strip()

            data = json.loads(response_text)

            narrative = data.get("narrative", "The AI did not provide a narrative.")
            updates_dict = data.get("game_state_updates", {})

            game_state_updates = GameStateUpdates(**updates_dict)

            return narrative, game_state_updates

        except json.JSONDecodeError as e:
            error_message = f"AI response was not valid JSON: {e}\nRaw AI response: {original_response_text_for_debugging}"
            print(error_message)
            return original_response_text_for_debugging, GameStateUpdates()

        except Exception as e:
            error_message = f"An unexpected error occurred while getting AI response: {e}"
            print(error_message)
            # Use original_response_text_for_debugging if available, otherwise the error_message itself
            narrative_error = original_response_text_for_debugging if original_response_text_for_debugging else error_message
            return narrative_error, GameStateUpdates()

if __name__ == '__main__':
    # Example Usage (requires GOOGLE_API_KEY to be set in the environment or passed directly)
    # Ensure you have the google-generativeai and pydantic packages installed
    print("Attempting to initialize AIDungeonMaster...")

    # --- Mock classes for testing ---
    class MockResponse:
        def __init__(self, text):
            self.text = text

    class MockModel:
        def __init__(self, model_name='gemini-2.0-flash-lite'):
            self.model_name = model_name

        def generate_content(self, prompt_string):
            print("(MockModel received prompt, returning mock JSON response)")
            # Simulate a JSON response based on the new concise prompt's examples
            if "curse" in prompt_string: # Crude way to pick an example based on player action
                mock_json_payload = {
                    "narrative": "You feel weaker after the Asura's curse and notice your favorite dagger is gone, but you find a healing herb.",
                    "game_state_updates": {
                        "inventory_add": ["healing herb"],
                        "inventory_remove": ["favorite dagger"],
                        "hp_change": -10,
                        "mp_change": -5,
                        "new_story_flags": {"cursed": True},
                        "player_name": "Weakened Player"
                    }
                }
            else: # Default mock
                mock_json_payload = {
                    "narrative": "This is a mock narrative for other actions.",
                    "game_state_updates": {
                        "inventory_add": ["mock item"],
                        "hp_change": -5,
                        "new_story_flags": {"mock_flag_set": True},
                        "player_name": "MockHeroName"
                    }
                }
            # Simulate AI wrapping the response in markdown ```json ... ```
            raw_response_with_fences = f"```json\n{json.dumps(mock_json_payload)}\n```"
            return MockResponse(text=raw_response_with_fences)

    class MockPlayer:
        def __init__(self, name, hp, max_hp, mp, max_mp, current_location, story_flags, inventory):
            self.name = name
            self.hp = hp
            self.max_hp = max_hp
            self.mp = mp
            self.max_mp = max_mp
            self.current_location = current_location
            self.story_flags = story_flags
            self.inventory = inventory
    # --- End Mock classes ---

    try:
        dm = AIDungeonMaster(api_key="FAKE_API_KEY_FOR_TESTING")
        dm.model = MockModel()

        print("AIDungeonMaster initialized with MockModel successfully.")

        initial_scene = "You find yourself in a dimly lit antechamber. The air is heavy with the scent of incense."
        print("\nInitial Scene (Assumed for test):")
        print(initial_scene)

        print("\n--- Simulating Player Action (expecting comprehensive update from mock) ---")
        player_input_action = "I touch the cursed idol." # Action to trigger specific mock
        print(f"Player action: {player_input_action}")

        test_player = MockPlayer(
            name="TestHero", hp=90, max_hp=100, mp=40, max_mp=50,
            current_location=initial_scene.splitlines()[0],
            story_flags={"found_dagger": False, "met_sage": True},
            inventory=["a rusty sword", "some dried rations", "a mysterious amulet", "favorite dagger"]
        )

        narrative, game_updates = dm.get_ai_response(player_object=test_player, player_action=player_input_action)

        print("\n--- Parsed AI Response ---")
        print("Narrative:")
        print(narrative)
        print("\nGame State Updates:")
        print(f"  Inventory Add: {game_updates.inventory_add}")
        print(f"  Inventory Remove: {game_updates.inventory_remove}")
        print(f"  HP Change: {game_updates.hp_change}")
        print(f"  MP Change: {game_updates.mp_change}")
        print(f"  New Story Flags: {game_updates.new_story_flags}")
        print(f"  New Location: {game_updates.new_location}")
        print(f"  Player Name: {game_updates.player_name}")


        print("\n--- Simulating Player Action (expecting minimal update from mock) ---")
        player_input_action_minimal = "I look around."
        print(f"Player action: {player_input_action_minimal}")

        # Reconfigure MockModel for minimal response (Example 2 type)
        dm.model.generate_content = lambda prompt_string: MockResponse(
            text=f"```json\n{json.dumps({'narrative': 'You look around but find nothing of interest, and nothing about you changes.', 'game_state_updates': {}})}\n```"
        )
        narrative_minimal, game_updates_minimal = dm.get_ai_response(player_object=test_player, player_action=player_input_action_minimal)
        print("\n--- Parsed AI Response (Minimal Update) ---")
        print("Narrative:")
        print(narrative_minimal)
        print("\nGame State Updates (should be all defaults):")
        print(f"  Inventory Add: {game_updates_minimal.inventory_add}")
        print(f"  Inventory Remove: {game_updates_minimal.inventory_remove}")
        print(f"  HP Change: {game_updates_minimal.hp_change}")
        print(f"  MP Change: {game_updates_minimal.mp_change}")
        print(f"  New Story Flags: {game_updates_minimal.new_story_flags}")
        print(f"  New Location: {game_updates_minimal.new_location}")
        print(f"  Player Name: {game_updates_minimal.player_name}")


        print("\n--- Simulating another player action (e.g., AI returns malformed JSON) ---")
        player_input_action_2 = "I try to decipher the ancient text."
        print(f"Player action: {player_input_action_2}")

        dm.model.generate_content = lambda prompt_string: MockResponse(text="This is not valid JSON {oops")

        narrative_2, game_updates_2 = dm.get_ai_response(player_object=test_player, player_action=player_input_action_2)
        print("\n--- Parsed AI Response (Malformed JSON Test) ---")
        print("Narrative:")
        print(narrative_2)
        print("\nGame State Updates (should be default/empty):")
        print(f"  Inventory Add: {game_updates_2.inventory_add}")
        print(f"  Player Name: {game_updates_2.player_name}")

        print("\n--- Simulating Player Action (JSON wrapped in ```) ---")
        player_input_action_3 = "Test with triple backticks"
        print(f"Player action: {player_input_action_3}")

        mock_json_payload_for_test3 = { # Re-define for clarity as it's a distinct test
            "narrative": "Narrative for triple-backtick test.",
            "game_state_updates": {
                "inventory_add": ["triple-backtick item"],
                "mp_change": 10,
                "player_name": "HeroStillMock"
            }
        }
        dm.model.generate_content = lambda prompt_string: MockResponse(text=f"```\n{json.dumps(mock_json_payload_for_test3)}\n```")

        narrative_3, game_updates_3 = dm.get_ai_response(player_object=test_player, player_action=player_input_action_3)
        print("\n--- Parsed AI Response (Triple Backticks Test) ---")
        print("Narrative:")
        print(narrative_3)
        print("\nGame State Updates:")
        print(f"  Inventory Add: {game_updates_3.inventory_add}")
        print(f"  Inventory Remove: {game_updates_3.inventory_remove}")
        print(f"  HP Change: {game_updates_3.hp_change}")
        print(f"  MP Change: {game_updates_3.mp_change}")
        print(f"  New Story Flags: {game_updates_3.new_story_flags}")
        print(f"  New Location: {game_updates_3.new_location}")
        print(f"  Player Name: {game_updates_3.player_name}")

    except ValueError as e:
        print(f"Error during example execution: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during example execution: {e}")

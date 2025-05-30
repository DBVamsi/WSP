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

Your response MUST be a valid JSON object.
The JSON object must have two top-level keys:
1.  `"narrative"`: A string describing what happens next in 3-5 concise sentences. This narrative should be creative, maintain the Indian Mythology theme, and consider the player's current situation, inventory, and known story flags.
2.  `"game_state_updates"`: A JSON object detailing any changes to the player's state or game world. If no change occurs for a particular aspect, omit the key or set its value to a default "no-change" state (e.g., 0 for hp_change, empty list for inventory_add/remove, null for new_location).

The `"game_state_updates"` object can contain the following keys:
    -   `"inventory_add"`: (list of strings) Items added to the player's inventory. Example: `["celestial sword", "healing potion"]`. Default: `[]`.
    -   `"inventory_remove"`: (list of strings) Items removed from the player's inventory. Example: `["broken shield"]`. Default: `[]`.
    -   `"hp_change"`: (integer) Change in player's HP (e.g., -10 for damage, 20 for healing). Default: `0`.
    -   `"mp_change"`: (integer) Change in player's MP. Default: `0`.
    -   `"new_story_flags"`: (object) New story flags to be set or updated. Example: `{{"met_sage": true, "artifact_found": false}}`. Default: `{}`.
    -   `"new_location"`: (string or null) The new location of the player, if they moved. Example: `"The Enchanted Forest"`. Default: `null`.

Example of a complete JSON response:
```json
{{
    "narrative": "You skillfully parry the Asura's attack with your dagger and find an opening. With a swift movement, you pick up a discarded healing potion from a fallen warrior.",
    "game_state_updates": {{
        "inventory_add": ["healing potion"],
        "inventory_remove": [],
        "hp_change": 0,
        "mp_change": 0,
        "new_story_flags": {{}},
        "new_location": null
    }}
}}
```

Another example (if player takes damage and uses an item):
```json
{{
    "narrative": "The Asura's blow lands, and you feel a searing pain. You quickly quaff your healing herb, and its magic soothes some of your wounds.",
    "game_state_updates": {{
        "inventory_add": [],
        "inventory_remove": ["healing herb"],
        "hp_change": -15,
        "mp_change": 0,
        "new_story_flags": {{}},
        "new_location": null
    }}
}}
```
Remember to only include keys in `game_state_updates` if their values actually change. Ensure your output is a single, valid JSON object.
"""
        response_text = ""
        try:
            # Log the prompt that will be sent
            print(f"--- PROMPT SENT TO AI (expecting JSON response) ---\n{prompt_string}\n-------------------------")

            response = self.model.generate_content(prompt_string)
            response_text = response.text

            # Attempt to parse the entire response_text as JSON
            data = json.loads(response_text)

            narrative = data.get("narrative", "The AI did not provide a narrative.") # Default narrative
            updates_dict = data.get("game_state_updates", {})

            game_state_updates = GameStateUpdates(**updates_dict) # Validate and structure with Pydantic

            return narrative, game_state_updates

        except json.JSONDecodeError as e:
            error_message = f"AI response was not valid JSON: {e}\nRaw AI response: {response_text}"
            print(error_message)
            # Fallback: return the raw response text as narrative, and default (empty) updates
            return response_text, GameStateUpdates()

        except Exception as e: # Catch other potential errors (e.g., network issues, API errors)
            error_message = f"An unexpected error occurred while getting AI response: {e}"
            print(error_message)
            narrative_error = response_text if response_text else error_message
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
            # Simulate a JSON response
            mock_json_payload = {
                "narrative": "This is a mock narrative from the AI.",
                "game_state_updates": {
                    "inventory_add": ["mock item"],
                    "hp_change": -5,
                    "new_story_flags": {"mock_flag_set": True}
                }
            }
            return MockResponse(text=json.dumps(mock_json_payload))

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
        # Replace real AI DM with a mock for predictable testing without API key
        dm = AIDungeonMaster(api_key="FAKE_API_KEY_FOR_TESTING") # api_key is mandatory
        dm.model = MockModel() # Replace the actual model with our mock

        print("AIDungeonMaster initialized with MockModel successfully.")

        # Initial scene description (can also be mocked if needed, but not the focus here)
        # print("\nAttempting to get initial scene description...")
        # initial_scene = dm.get_initial_scene_description() # This would use the real model if not overridden
        # For this test, let's assume a generic initial scene:
        initial_scene = "You find yourself in a dimly lit antechamber. The air is heavy with the scent of incense."
        print("\nInitial Scene (Assumed for test):")
        print(initial_scene)

        print("\n--- Simulating Player Action ---")
        player_input_action = "I examine the strange markings on the wall."
        print(f"Player action: {player_input_action}")

        test_player = MockPlayer(
            name="TestHero", hp=90, max_hp=100, mp=40, max_mp=50,
            current_location=initial_scene.splitlines()[0],
            story_flags={"found_dagger": False, "met_sage": True},
            inventory=["a rusty sword", "some dried rations", "a mysterious amulet"]
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

        print("\n--- Simulating another player action (e.g., AI returns malformed JSON) ---")
        player_input_action_2 = "I try to decipher the ancient text."
        print(f"Player action: {player_input_action_2}")

        # Configure MockModel to return malformed JSON for the next call
        dm.model.generate_content = lambda prompt_string: MockResponse(text="This is not valid JSON {oops")

        narrative_2, game_updates_2 = dm.get_ai_response(player_object=test_player, player_action=player_input_action_2)
        print("\n--- Parsed AI Response (Malformed JSON Test) ---")
        print("Narrative:")
        print(narrative_2) # Should contain the error message and raw response
        print("\nGame State Updates (should be default/empty):")
        print(f"  Inventory Add: {game_updates_2.inventory_add}")


    except ValueError as e:
        print(f"Error during example execution: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during example execution: {e}")

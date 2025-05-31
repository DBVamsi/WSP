import google.generativeai as genai
import os # For potentially loading API key from environment
import json # For parsing AI response
from game_engine.character_manager import Player # For type hinting
from .common_types import GameStateUpdates, AdventureLog, AdventureLogEntry # For structuring game state updates and adventure log

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
Player's skills: {str(player_object.skills) if hasattr(player_object, 'skills') else 'None'}.
Key story events/flags known so far: {str(player_object.story_flags)}.

The player says: "{player_action}"

Combat Instructions:
- You can introduce hostile NPCs or creatures, initiating combat.
- If combat occurs, describe the enemy, its actions, and the environment.
- Player actions during combat could be 'attack [target]', 'use [skill name] [on target/on self]', 'defend', 'flee', etc.
- When the player or an enemy takes damage, or an enemy is defeated, reflect this in the narrative and use `game_state_updates` (especially `hp_change` for the player) for mechanical effects.
- You are responsible for tracking enemy health and status narratively.

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
    -   `"skill_used"`: str | null - The skill the player successfully used. Default: null.

Example 1 (Comprehensive update with skill usage):
```json
{{
    "narrative": "Focusing your will, you unleash a Power Attack against the charging Rakshasa! It stumbles back, wounded. You feel drained but victorious.",
    "game_state_updates": {{
        "mp_change": -15,
        "skill_used": "Power Attack",
        "new_story_flags": {{"rakshasa_wounded": true}}
    }}
}}
```
Example 2 (Simple item discovery, no skill):
```json
{{
    "narrative": "You search the old chest and find a glowing gem inside.",
    "game_state_updates": {{
        "inventory_add": ["glowing gem"],
        "new_story_flags": {{"found_gem": true}}
    }}
}}
```
Example 3 (Narrative only, no state changes):
```json
{{
    "narrative": "You look around but find nothing of interest, and nothing about you changes.",
    "game_state_updates": {{}}
}}
```
Example 4 (Combat scenario):
Player action: "I attack the goblin with my sword."
```json
{{
    "narrative": "You swing your sword at the goblin, landing a glancing blow. The goblin shrieks and lunges with its rusty dagger, catching your arm!",
    "game_state_updates": {{
        "hp_change": -5
    }}
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

    def get_scene_description_from_log(self, player_object: Player) -> str:
        """
        Generates a scene description for a continued game based on the player's adventure log.
        """
        if not player_object.adventure_log or not player_object.adventure_log.entries:
            # This case should ideally be handled by GameManager, but as a safeguard:
            print("AI_DM: get_scene_description_from_log called with empty or no log. Falling back to initial scene logic.")
            return self.get_initial_scene_description()

        # Format the adventure log entries for the prompt
        log_summary = "\n".join([
            f"- Turn {entry.turn_number} ({entry.type}): {entry.content}"
            for entry in player_object.adventure_log.entries
        ])

        prompt_string = f"""You are a Dungeon Master for a text-based RPG set in a world inspired by Indian Mythology, focusing on a great war between Devas and Asuras.
The player, {player_object.name}, is resuming their adventure.
Here's a summary of what happened recently (The Adventure Log):
{log_summary}

Current Player Status:
- HP: {player_object.hp}/{player_object.max_hp}
- MP: {player_object.mp}/{player_object.max_mp}
- Location: {player_object.current_location}
- Inventory: {str(player_object.inventory if hasattr(player_object, 'inventory') else [])}
- Skills: {str(player_object.skills) if hasattr(player_object, 'skills') else 'None'}
- Key Story Flags: {str(player_object.story_flags)}

Based on this log and the player's current state, provide a brief (2-3 concise sentences) re-orienting narrative to smoothly continue their adventure. This narrative should bridge from the last log entry and set the immediate scene. Do not ask questions, just describe the situation.
"""
        try:
            print(f"--- PROMPT SENT TO AI (for continuation) ---\n{prompt_string}\n-------------------------")
            response = self.model.generate_content(prompt_string)
            # Consider adding more robust error checking for response if needed,
            # e.g., checking response.prompt_feedback for block reasons.
            if response.text:
                return response.text
            else:
                # Handle cases where response.text might be empty or None if API behaves unexpectedly
                print('AI DM: Received empty response for continuation prompt.')
                return "The threads of fate are tangled. You find yourself in a familiar yet subtly changed setting..." # Fallback
        except Exception as e:
            print(f'Error contacting AI DM for continuation scene: {e}')
            return 'Error: The mists of time swirl, obscuring your path forward for a moment... Please try again or check your connection.'

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
            self.last_prompt = "" # For debugging

        def generate_content(self, prompt_string):
            self.last_prompt = prompt_string
            print(f"\n--- MockModel received prompt string for evaluation: ---\n{prompt_string}\n---------------------------------------------------\n")
            print("(MockModel logic: evaluating which mock response to return based on prompt content...)")
            if "Player's skills:" not in prompt_string: # This check is fine
                print("WARNING: 'Player's skills:' not found in the prompt to MockModel (this might be ok for initial scene calls if any).")

            # Simulate a JSON response based on player action
            # Order of checks matters if prompts could contain multiple keywords.
            if "resuming their adventure" in prompt_string: # Check for continuation prompt
                print("DEBUG: MockModel matched 'resuming their adventure' for get_scene_description_from_log")
                return MockResponse(text="Mock: The air crackles with anticipation as you step back into the fray. The path ahead is clear.")
            elif "curse" in prompt_string:
                print("DEBUG: MockModel matched 'curse'")
                mock_json_payload = {
                    "narrative": "Mock: You feel weaker after the Asura's curse and notice your favorite dagger is gone, but you find a healing herb.",
                    "game_state_updates": {
                        "inventory_add": ["healing herb"],
                        "inventory_remove": ["favorite dagger"],
                        "hp_change": -10,
                        "mp_change": -5,
                        "new_story_flags": {"cursed": True},
                    }
                }
            elif "use Power Attack" in prompt_string:
                print("DEBUG: MockModel matched 'use Power Attack'")
                mock_json_payload = {
                    "narrative": "Mock: You unleash a mighty Power Attack! The enemy is stunned.",
                    "game_state_updates": {
                        "mp_change": -10,
                        "skill_used": "Power Attack",
                        "new_story_flags": {"enemy_stunned": True}
                    }
                }
            elif "attack the goblin" in prompt_string: # New mock for combat
                print("DEBUG: MockModel matched 'attack the goblin'")
                mock_json_payload = {
                    "narrative": "Mock: You swing your sword at the goblin, landing a glancing blow. The goblin shrieks and lunges with its rusty dagger, catching your arm!",
                    "game_state_updates": {
                        "hp_change": -5
                    }
                }
            else: # Default mock
                print("DEBUG: MockModel matched default")
                mock_json_payload = {
                    "narrative": "Mock: This is a mock narrative for other actions (default).",
                    "game_state_updates": {
                        "inventory_add": ["mock item"],
                        "hp_change": -5, # Default hp_change
                        "new_story_flags": {"mock_flag_set_default": True}
                    }
                }
            raw_response_with_fences = f"```json\n{json.dumps(mock_json_payload)}\n```"
            return MockResponse(text=raw_response_with_fences)

    class MockPlayer:
        def __init__(self, name, hp, max_hp, mp, max_mp, current_location, story_flags, inventory, skills=None, adventure_log=None):
            self.name = name
            self.hp = hp
            self.max_hp = max_hp
            self.mp = mp
            self.max_mp = max_mp
            self.current_location = current_location
            self.story_flags = story_flags
            self.inventory = inventory
            self.skills = skills if skills is not None else ["Default Skill 1", "Default Skill 2"]
            self.adventure_log = adventure_log if adventure_log is not None else AdventureLog() # Initialize log
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
            current_location="Dimly Lit Antechamber", # Simplified for test
            story_flags={"found_dagger": False, "met_sage": True},
            inventory=["a rusty sword", "some dried rations", "a mysterious amulet", "favorite dagger"],
            skills=["Power Attack", "Meditate", "Quick Dodge"]
        )
        # Update dm.model.generate_content to use the specific instance of MockModel
        mock_model_instance = MockModel()
        dm.model = mock_model_instance # Assign the instance

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
        print(f"  Skill Used: {game_updates.skill_used}") # Should be None for this case
        if "Combat Instructions:" not in dm.model.last_prompt:
             print("ERROR: Combat instructions missing in prompt for 'cursed idol' test!")


        print("\n--- Simulating Player Action (Skill Usage) ---")
        player_action_skill = "I use Power Attack on the guard!"
        print(f"Player action: {player_action_skill}")

        # The same mock_model_instance will be used, its behavior changes based on prompt content
        narrative_skill, game_updates_skill = dm.get_ai_response(player_object=test_player, player_action=player_action_skill)

        print("\n--- Parsed AI Response (Skill Usage) ---")
        print("Narrative:")
        print(narrative_skill)
        print("\nGame State Updates:")
        print(f"  MP Change: {game_updates_skill.mp_change}") # Should show -10 from mock
        print(f"  Skill Used: {game_updates_skill.skill_used}") # Should now be 'Power Attack'
        print(f"  New Story Flags: {game_updates_skill.new_story_flags}")
        if "Combat Instructions:" not in dm.model.last_prompt:
             print("ERROR: Combat instructions missing in prompt for 'Power Attack' test!")


        print("\n--- Simulating Player Action (Combat) ---")
        player_action_combat = "I attack the goblin with my sword."
        print(f"Player action: {player_action_combat}")
        narrative_combat, game_updates_combat = dm.get_ai_response(player_object=test_player, player_action=player_action_combat)

        print("\n--- Parsed AI Response (Combat) ---")
        print("Narrative:")
        print(narrative_combat)
        print("\nGame State Updates:")
        print(f"  HP Change: {game_updates_combat.hp_change}") # Should be -5 from mock
        print(f"  Skill Used: {game_updates_combat.skill_used}") # Should be None
        if "Combat Instructions:" not in dm.model.last_prompt:
             print("ERROR: Combat instructions missing in prompt for 'attack goblin' test!")


        print("\n--- Simulating Player Action (expecting minimal update from mock) ---")
        player_input_action_minimal = "I look around."
        print(f"Player action: {player_input_action_minimal}")

        # Temporarily override generate_content for this specific test case
        original_generate_content = dm.model.generate_content
        dm.model.generate_content = lambda prompt_string: MockResponse(
            text=f"```json\n{json.dumps({'narrative': 'Mock: You look around but find nothing of interest, and nothing about you changes.', 'game_state_updates': {}})}\n```"
        )
        narrative_minimal, game_updates_minimal = dm.get_ai_response(player_object=test_player, player_action=player_input_action_minimal)
        dm.model.generate_content = original_generate_content # Restore original mock behavior

        print("\n--- Parsed AI Response (Minimal Update) ---")
        print("Narrative:")
        print(narrative_minimal)
        print("\nGame State Updates (should be all defaults):")
        print(f"  Inventory Add: {game_updates_minimal.inventory_add}")
        print(f"  MP Change: {game_updates_minimal.mp_change}")
        print(f"  New Story Flags: {game_updates_minimal.new_story_flags}")
        print(f"  Skill Used: {game_updates_minimal.skill_used}") # Should be None


        print("\n--- Simulating another player action (e.g., AI returns malformed JSON) ---")
        player_input_action_malformed = "I try to decipher the ancient text."
        print(f"Player action: {player_input_action_malformed}")

        original_generate_content_malformed = dm.model.generate_content
        dm.model.generate_content = lambda prompt_string: MockResponse(text="This is not valid JSON {oops")
        narrative_malformed, game_updates_malformed = dm.get_ai_response(player_object=test_player, player_action=player_input_action_malformed)
        dm.model.generate_content = original_generate_content_malformed # Restore

        print("\n--- Parsed AI Response (Malformed JSON Test) ---")
        print("Narrative:")
        print(narrative_malformed)
        print("\nGame State Updates (should be default/empty):")
        print(f"  Inventory Add: {game_updates_malformed.inventory_add}")
        print(f"  Player Name: {game_updates_malformed.player_name}")
        print(f"  Skill Used: {game_updates_malformed.skill_used}") # Should be None

        print("\n--- Testing get_scene_description_from_log ---")
        player_with_log = MockPlayer(
            name="LogHero", hp=80, max_hp=100, mp=30, max_mp=50,
            current_location="Old Temple",
            story_flags={"found_relic": True},
            inventory=["torch", "map"],
            skills=["Heal Self"],
            adventure_log=AdventureLog(max_entries=5) # Use a smaller max for test
        )
        # Add some entries to the log
        player_with_log.adventure_log.entries.append(AdventureLogEntry(type="player_action", content="Entered the dark cave", turn_number=1))
        player_with_log.adventure_log.entries.append(AdventureLogEntry(type="ai_output", content="The cave is damp and silent. A faint glow ahead.", turn_number=1))
        player_with_log.adventure_log.entries.append(AdventureLogEntry(type="player_action", content="Investigate the glow", turn_number=2))
        player_with_log.adventure_log.entries.append(AdventureLogEntry(type="ai_output", content="You found a hidden inscription!", turn_number=2))

        continuation_scene = dm.get_scene_description_from_log(player_with_log)
        print("\n--- Continuation Scene from Log ---")
        print(continuation_scene)

        print("\n--- Testing get_scene_description_from_log (empty log) ---")
        player_empty_log = MockPlayer(
            name="FreshHero", hp=100, max_hp=100, mp=50, max_mp=50,
            current_location="Starting Village",
            story_flags={},
            inventory=[],
            adventure_log=AdventureLog() # Empty log
        )
        # Temporarily make MockModel return a specific string for initial scene to verify fallback
        original_generate_content_initial = dm.model.generate_content
        def mock_initial_scene_for_empty_log_test(prompt_string):
            if "Describe the very first intriguing scene" in prompt_string:
                 print("DEBUG: MockModel matched 'Describe the very first intriguing scene' for empty log test")
                 return MockResponse(text="Mock: You stand at a crossroads, ready for a new adventure (empty log fallback).")
            return original_generate_content_initial(prompt_string) # Call original mock for other prompts

        dm.model.generate_content = mock_initial_scene_for_empty_log_test
        initial_scene_for_empty_log = dm.get_scene_description_from_log(player_empty_log)
        dm.model.generate_content = original_generate_content_initial # Restore
        print("\n--- Initial Scene for Empty Log (Fallback Test) ---")
        print(initial_scene_for_empty_log)


    except ValueError as e:
        print(f"Error during example execution: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during example execution: {e}")

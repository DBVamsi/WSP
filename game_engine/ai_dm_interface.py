import google.generativeai as genai
import os # For potentially loading API key from environment
from game_engine.character_manager import Player # For type hinting

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

    def get_ai_response(self, player_object: Player, player_action: str) -> str:
        """
        Generates and returns the AI DM's response to a player's action,
        considering the player's current state.

        Args:
            player_object (Player): The player character object.
            player_action (str): The action taken by the player.

        Returns:
            str: The AI DM's narrative response to the player's action, or an error message.
        """
        prompt_string = f"""You are the Dungeon Master for a text-based RPG inspired by Indian Mythology, focusing on a great war between Devas and Asuras.
The player is {player_object.name}.
Player's current status: HP: {player_object.hp}/{player_object.max_hp}, MP: {player_object.mp}/{player_object.max_mp}.
Player's current location: {player_object.current_location}.
Key story events/flags known so far: {str(player_object.story_flags)}.

The player says: "{player_action}"

Describe what happens next in 3-5 concise sentences. Be creative, maintain the Indian Mythology theme, and consider the player's current situation and known story flags.
"""
        try:
            response = self.model.generate_content(prompt_string)
            # Consider adding more robust error checking for response if needed
            return response.text
        except Exception as e:
            print(f'Error contacting AI DM (player action): {e}')
            return 'Error: The threads of fate are tangled... Please try again.'

if __name__ == '__main__':
    # Example Usage (requires GOOGLE_API_KEY to be set in the environment)
    # Ensure you have the google-generativeai package installed: pip install google-generativeai
    print("Attempting to initialize AIDungeonMaster...")
    try:
        # To run this example, make sure your GOOGLE_API_KEY is set in your environment
        # For example, in your terminal: export GOOGLE_API_KEY="YOUR_API_KEY"
        # Or pass it directly: dm = AIDungeonMaster(api_key="YOUR_API_KEY")

        # Attempt to load API key from environment if not directly passed for this example
        if not os.getenv("GOOGLE_API_KEY"):
            print("Warning: GOOGLE_API_KEY environment variable is not set.")
            print("Skipping AIDungeonMaster initialization example.")
        else:
            dm = AIDungeonMaster() # API key loaded from environment
            print("AIDungeonMaster initialized successfully.")

            # Updated check for the new model name
            if "gemini-2.0-flash-lite" in dm.model.model_name:
                 print(f"Successfully initialized model: {dm.model.model_name}")
            else:
                 print(f"Model name unexpected: {dm.model.model_name}")

            print("\nAttempting to get initial scene description...")
            initial_scene = dm.get_initial_scene_description()
            print("\nInitial Scene:")
            print(initial_scene)

            print("\n--- Simulating Player Action ---")
            player_input_action = "I look for a weapon."
            print(f"Player action: {player_input_action}")

            # Create a dummy Player object for the test
            # In a real game, this would be the actual player object from GameManager
            class MockPlayer: # Define a simple mock for testing if Player class is not fully available/integrated here
                def __init__(self, name, hp, max_hp, mp, max_mp, current_location, story_flags):
                    self.name = name
                    self.hp = hp
                    self.max_hp = max_hp
                    self.mp = mp
                    self.max_mp = max_mp
                    self.current_location = current_location
                    self.story_flags = story_flags

            test_player = MockPlayer(
                name="TestHero", hp=90, max_hp=100, mp=40, max_mp=50,
                current_location=initial_scene.splitlines()[0] if "Error:" not in initial_scene else "A mysterious cave", # Use first line of scene
                story_flags={"found_dagger": False, "met_sage": True}
            )
            if "Error:" in initial_scene:
                 test_player.current_location = "The edge of a swirling vortex of cosmic energy"


            ai_narrative = dm.get_ai_response(player_object=test_player, player_action=player_input_action)
            print("\nAI DM's Response:")
            print(ai_narrative)

            player_input_action_2 = "I try to meditate to sense my surroundings."
            print(f"\nPlayer action: {player_input_action_2}")

            # Update mock player based on previous response if needed, or keep static for this test
            if "Error:" not in ai_narrative :
                test_player.current_location = "A place altered by previous actions" # Example update
                test_player.story_flags["sensed_danger"] = True

            ai_narrative_2 = dm.get_ai_response(player_object=test_player, player_action=player_input_action_2)
            print("\nAI DM's Response:")
            print(ai_narrative_2)


    except ValueError as e:
        print(f"Error initializing AIDungeonMaster: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during example execution: {e}")
        print("Please ensure google-generativeai is installed and GOOGLE_API_KEY is set correctly.")

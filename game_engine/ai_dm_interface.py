import google.generativeai as genai
import os # For potentially loading API key from environment

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
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
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

    def get_ai_response(self, player_action: str, current_context: str = 'The player is in an area previously described.') -> str:
        """
        Generates and returns the AI DM's response to a player's action.

        Args:
            player_action (str): The action taken by the player.
            current_context (str, optional): The current context or situation of the game.
                                             Defaults to 'The player is in an area previously described.'.

        Returns:
            str: The AI DM's narrative response to the player's action, or an error message.
        """
        prompt_string = (
            f'You are the Dungeon Master for a text-based RPG set in a world inspired by Indian Mythology. '
            f'The current situation is: {current_context}. '
            f'The player says: "{player_action}". '
            f'Describe what happens next in 2-4 concise sentences, keeping the mythology theme in mind.'
        )
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

            if "gemini-1.5-flash" in dm.model.model_name:
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
            # Use the initial scene as context, or a more specific one if available
            context_for_action = initial_scene
            if "Error:" in initial_scene: # If initial scene failed, use a generic context
                context_for_action = "The player is standing at the precipice of adventure, the air thick with anticipation."

            ai_narrative = dm.get_ai_response(player_action=player_input_action, current_context=context_for_action)
            print("\nAI DM's Response:")
            print(ai_narrative)

            player_input_action_2 = "I try to meditate to sense my surroundings."
            print(f"\nPlayer action: {player_input_action_2}")
            context_for_action_2 = ai_narrative # Use previous AI response as new context
            if "Error:" in ai_narrative:
                 context_for_action_2 = "Despite the previous error, the player tries to focus."

            ai_narrative_2 = dm.get_ai_response(player_action=player_input_action_2, current_context=context_for_action_2)
            print("\nAI DM's Response:")
            print(ai_narrative_2)


    except ValueError as e:
        print(f"Error initializing AIDungeonMaster: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during example execution: {e}")
        print("Please ensure google-generativeai is installed and GOOGLE_API_KEY is set correctly.")

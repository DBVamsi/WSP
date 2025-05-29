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

    except ValueError as e:
        print(f"Error initializing AIDungeonMaster: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during example execution: {e}")
        print("Please ensure google-generativeai is installed and GOOGLE_API_KEY is set correctly.")

import eel

class WebUIManager:
    def __init__(self):
        self.is_ready = False # Flag to check if JS has signaled readiness
        print("WebUIManager: Initialized. Waiting for JS readiness signal.")

    def set_ready(self):
        print("WebUIManager: JavaScript has signaled readiness.")
        self.is_ready = True
        # Optionally, send initial game state or welcome message here if needed
        # For now, let's ensure the game manager triggers initial display after player load.

    def add_story_text(self, text: str, msg_type: str = 'normal'):
        if self.is_ready:
            # Python's multiline strings will contain literal '\n'.
            # The JS function update_narrative now expects to split text_line by '\\n' (literal backslash n)
            # if Python sends it that way, or by '\n' (newline character) if Python sends that.
            # Let's ensure Python newlines are passed as such, and JS handles them.
            # The JS from the previous step was: `const responseLines = sanitizedText.split('\\n');`
            # This means Python should send `text.replace('\n', '\\n')`.
            # However, the prompt for *this* subtask says:
            # "Let's assume direct \n works for now and remove the replace call to simplify."
            # This implies JS `split('\n')` should be used.
            # The JS from previous step had:
            # `const responseLines = sanitizedText.split('\\n');` for command_response
            # `const normalLines = sanitizedText.split('\\n');` for normal
            # This means Python *should* send `text.replace('\n','\\n')` for those JS functions to work as written.
            # Let's stick to the instruction to REMOVE the replace for now and assume JS will be adapted if needed,
            # or that Python's `\n` will be interpreted by JS's `split('\n')` if the JS is changed.
            # For maximum clarity, if JS is `split('\\n')`, Python MUST send `replace('\n', '\\n')`.
            # If JS is `split('\n')`, Python sends `text` directly.
            # The last JS `update_narrative` uses `sanitizedText.split('\\n')`.
            # So, Python needs to send `text.replace('\n', '\\\\n')` to make `\\n` a literal string for JS `split`.
            # OR, the JS needs to change `split('\\n')` to `split('\n')`.
            # The subtask says: "Let's assume direct \n works for now and remove the replace call".
            # This implies the JS should be using `split('\n')`. I will proceed with this assumption.
            # If the JS *actually* uses `split('\\n')`, then this Python code is "wrong" based on that JS.
            # But based on the instruction "remove the replace call", this is correct.
            eel.update_narrative(text, msg_type)
        else:
            # Max 100 chars for the log to keep it concise.
            text_snippet = text[:100] + "..." if len(text) > 100 else text
            print(f"WebUIManager: JS not ready. Story text (type: {msg_type}) not sent: {text_snippet}")


    def update_player_display(self, player): # player is a Player object
        if not self.is_ready or not player:
            player_name_for_log = "N/A"
            if player and hasattr(player, 'name'): # Check if player object exists and has name
                player_name_for_log = player.name
            elif player: # Player object exists but no name attribute
                player_name_for_log = "Unknown Player (no name attr)"

            print(f"DEBUG WebUIManager: JS not ready or no player. Player display update skipped. is_ready={self.is_ready}, player_exists={player is not None} (Name: {player_name_for_log})")
            return

        print(f"DEBUG WebUIManager: update_player_display called. Player type: {type(player)}")
        # Ensure all attributes are accessed safely, providing defaults if necessary
        hp = getattr(player, 'hp', 'N/A')
        max_hp = getattr(player, 'max_hp', 'N/A')
        mp = getattr(player, 'mp', 'N/A')
        max_mp = getattr(player, 'max_mp', 'N/A')
        location = getattr(player, 'current_location', 'N/A')
        inventory = getattr(player, 'inventory', []) # Default to empty list for logging
        skills = getattr(player, 'skills', [])       # Default to empty list for logging
        name = getattr(player, 'name', 'N/A')

        print(f"DEBUG WebUIManager: Received player data: Name='{name}', HP={hp}/{max_hp}, MP={mp}/{max_mp}, Loc='{location}', Inv={inventory}, Skills={skills}")

        # Log values just before sending to JS for stats
        print(f"DEBUG WebUIManager: Calling eel.update_player_stats with: HP={hp}, MaxHP={max_hp}, MP={mp}, MaxMP={max_mp}, Loc='{location}'")
        eel.update_player_stats(
            hp, max_hp,
            mp, max_mp,
            location
        )

        # Log values for inventory
        inventory_to_send = getattr(player, 'inventory', []) # Ensure it's always a list for eel
        print(f"DEBUG WebUIManager: Calling eel.update_inventory with: {inventory_to_send}")
        eel.update_inventory(inventory_to_send)

        # Log values for skills
        skills_to_send = getattr(player, 'skills', []) # Ensure it's always a list for eel
        print(f"DEBUG WebUIManager: Calling eel.update_skills with: {skills_to_send}")
        eel.update_skills(skills_to_send)

        print("DEBUG WebUIManager: update_player_display finished all eel calls.")


    def get_player_input(self) -> str:
        # This method is effectively obsolete in the Eel architecture as input comes from JS.
        # GameManager should no longer call this.
        print("WebUIManager: get_player_input() was called, but this is deprecated in Eel UI. Input is JS-driven.")
        # Returning an empty string or raising an error are options.
        # For now, to avoid breaking existing GameManager logic that might still call it
        # before full refactoring, return empty. But ideally, it's not called.
        return ""

    def start_ui(self):
        # Eel's UI loop is managed by eel.start() in main.py.
        # This method is a no-op for Eel.
        print("WebUIManager: start_ui() called (no-op for Eel).")

    def quit_ui(self):
        # Eel window closing is handled by the user closing the window,
        # which causes eel.start() to return, or by Python exiting.
        print("WebUIManager: quit_ui() called (no-op for Eel).")

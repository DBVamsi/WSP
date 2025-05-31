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

    def add_story_text(self, text: str):
        if self.is_ready:
            eel.update_narrative(text)
        else:
            # This is a fallback for debugging; ideally, calls are made only when ready.
            print(f"WebUIManager: JS not ready. Story text not sent to UI: {text}")


    def update_player_display(self, player): # player is a Player object
        if self.is_ready and player:
            eel.update_player_stats(
                player.hp, player.max_hp,
                player.mp, player.max_mp,
                player.current_location
            )
            eel.update_inventory(player.inventory if hasattr(player, 'inventory') else [])
            eel.update_skills(player.skills if hasattr(player, 'skills') else [])
        elif not self.is_ready:
            print(f"WebUIManager: JS not ready. Player display update skipped for {player.name if player else 'Unknown Player'}.")
        elif not player:
            print(f"WebUIManager: No player object provided. Player display update skipped.")

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

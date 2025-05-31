import eel
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from game_engine.game_manager import GameManager
from ui.web_ui_manager import WebUIManager
# Import handlers and the descriptions dictionary
from main_eel_handlers import (
    js_ready_handler,
    process_player_command_handler,
    handle_map_click_handler,
    MAP_REGION_DESCRIPTIONS as imported_map_descriptions
)

# Global instances
web_ui_manager = WebUIManager()
game_manager: GameManager | None = None
# Make map descriptions available globally in this module if needed, or pass directly
MAP_REGION_DESCRIPTIONS = imported_map_descriptions

@eel.expose
def js_ready(message: str):
    """Called by JavaScript when the DOM and JS are ready. Delegates to handler."""
    print(f"Python (main.py): JS ready signal received: {message}")
    # web_ui_manager and game_manager are global here
    js_ready_handler(message, web_ui_manager, game_manager)

@eel.expose
def process_player_command_py(command_string: str):
    """Called by JavaScript when the player enters a command. Delegates to handler."""
    print(f"Python (main.py): Command received from JS: {command_string}")
    # game_manager is global here
    process_player_command_handler(command_string, game_manager)

@eel.expose
def handle_map_click_py(region_name: str):
    """Called by JavaScript when a defined map region is clicked. Delegates to handler."""
    print(f"Python (main.py): Map region clicked: {region_name}")
    # web_ui_manager is global, MAP_REGION_DESCRIPTIONS is also global in this module
    return handle_map_click_handler(region_name, web_ui_manager, MAP_REGION_DESCRIPTIONS)


def main_eel():
    global game_manager # Allow assignment to global game_manager

    script_dir = os.path.dirname(os.path.realpath(__file__))
    web_dir = os.path.join(script_dir, 'web')

    if not os.path.isdir(web_dir):
        print(f"Error: Web directory '{web_dir}' not found. Please ensure it exists.")
        return
    if not os.path.exists(os.path.join(web_dir, 'main.html')):
        print(f"Error: 'main.html' not found in '{web_dir}'.")
        return

    eel.init(web_dir)
    print(f"Main: Initializing Eel with web directory: {web_dir}")

    try:
        # Initialize GameManager with the WebUIManager
        game_manager = GameManager(ui_manager=web_ui_manager)
        print("Main: GameManager initialized successfully.")
    except Exception as e:
        print(f"Main: Error initializing GameManager: {e}")
        if web_ui_manager and hasattr(web_ui_manager, 'add_story_text') and web_ui_manager.is_ready:
            web_ui_manager.add_story_text(f"[Critical System Error: Failed to initialize GameManager: {e}]")
        return

    print("Main: Starting Eel app 'main.html'...")
    page_to_start = 'main.html'
    app_size = (1000, 750)

    try:
        eel.start(page_to_start, size=app_size)
    except (SystemExit, MemoryError, KeyboardInterrupt) as e:
        print(f"Main: Eel app closed or system error ({type(e).__name__}): {e}")
    except Exception as e:
        print(f"Main: An unexpected error occurred with Eel: {e}")

    print("Main: Game has finished or UI was closed. Application exiting.")
    if game_manager:
        # quit_game now calls sys.exit, so this will be the end of the script.
        game_manager.quit_game()

if __name__ == '__main__':
    main_eel()

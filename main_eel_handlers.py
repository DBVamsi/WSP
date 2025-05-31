# This file contains handler functions called by Eel-exposed functions in main.py.
# This helps in testing the logic without directly involving Eel's import-time behavior.

MAP_REGION_DESCRIPTIONS = {
    "The Old Well": "You peer into the Old Well. It's dark and seems to descend forever. A faint, cool breeze emanates from it.",
    "Mystic Forest Path": "The path leads into a dense, ancient forest. Sunlight struggles to penetrate the canopy, and strange sounds echo from the depths.",
    "Town Entrance": "A sturdy wooden gate marks the entrance to a small, bustling town. You can hear the sounds of merchants and see smoke rising from chimneys."
}

def js_ready_handler(message: str, web_ui_manager_instance, game_manager_instance):
    """Handles the js_ready signal."""
    print(f"Handler: JS ready signal received: {message}")
    if not web_ui_manager_instance:
        print("Handler Error: web_ui_manager_instance is None in js_ready_handler")
        return
    web_ui_manager_instance.set_ready()

    if game_manager_instance:
        game_manager_instance.initialize_game_state_and_ui()
    else:
        print("Handler Error: game_manager_instance is None in js_ready_handler")

def process_player_command_handler(command_string: str, game_manager_instance):
    """Handles processing player command."""
    print(f"Handler: Command received: {command_string}")
    if game_manager_instance:
        game_manager_instance.process_player_command_from_js(command_string)
    else:
        print("Handler Error: game_manager_instance is None in process_player_command_handler")
        # Optionally, try to send an error to UI if web_ui_manager is somehow available
        # This case indicates a severe setup issue.

def handle_map_click_handler(region_name: str, web_ui_manager_instance, descriptions_dict):
    """Handles map click events."""
    print(f"Handler: Map region clicked: {region_name}")

    description = descriptions_dict.get(region_name, f"You clicked on '{region_name}', but there's nothing more to see here right now.")
    message_to_display = f"You focus your attention on {region_name}.\n{description}"

    if web_ui_manager_instance and web_ui_manager_instance.is_ready:
        web_ui_manager_instance.add_story_text(message_to_display)
    else:
        # This case should ideally not happen if js_ready ensures ui is ready before clicks are processed.
        # However, as a fallback for direct calls or testing:
        print(f"Handler Warning: WebUIManager not ready or None. Cannot send map click message to UI: {message_to_display}")
        # If direct eel calling is desired as a fallback (though not ideal from handlers):
        # import eel # This would re-introduce eel import dependency here
        # if eel_is_available_somehow:
        #    eel.update_narrative(message_to_display.replace("\n", "<br>"))

    return f"Information for '{region_name}' displayed (from handler)."

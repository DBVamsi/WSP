import tkinter as tk
from tkinter import ttk # For themed widgets, if needed later
# It's good practice to import specific classes if you know them,
# but for now, tk.* is used.
# from tkinter import Label, Frame, Text, Entry, Button, Scrollbar, PanedWindow, Menu, messagebox, simpledialog
from game_engine.character_manager import Player # For type hinting (anticipated)

class GameUI:
    """
    Manages the main user interface for the Mythic Realms RPG.
    """
    def __init__(self, root, game_manager_ref):
        """
        Initializes the main game UI.

        Args:
            root: The root tkinter window.
            game_manager_ref: A reference to the GameManager instance.
        """
        self.root = root
        self.game_manager = game_manager_ref # Store the reference
        self.root.title('Mythic Realms RPG')
        self.root.geometry('1000x700')

        # Create and pack the main UI frames
        # Stats frame (left panel)
        self.stats_frame = tk.Frame(self.root, bg='grey', width=200) # Added width for visibility
        self.stats_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.stats_frame.pack_propagate(False) # Prevent resizing to fit content initially

        # Input frame (bottom panel)
        self.input_frame = tk.Frame(self.root, bg='darkgrey', height=100) # Added height for visibility
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_frame.pack_propagate(False) # Prevent resizing to fit content initially

        # Story frame (central panel)
        self.story_frame = tk.Frame(self.root, bg='black')
        self.story_frame.pack(expand=True, fill=tk.BOTH)
        # self.story_frame.pack_propagate(False) # Optional: if you want to control its size strictly

        # Stats display labels (replacing the temporary one)
        self.name_label = tk.Label(self.stats_frame, text="Name: ", background='grey', anchor='w')
        self.name_label.pack(anchor='w', fill='x', padx=5, pady=2)

        self.hp_label = tk.Label(self.stats_frame, text="HP: /", background='grey', anchor='w')
        self.hp_label.pack(anchor='w', fill='x', padx=5, pady=2)

        self.mp_label = tk.Label(self.stats_frame, text="MP: /", background='grey', anchor='w')
        self.mp_label.pack(anchor='w', fill='x', padx=5, pady=2)

        self.location_label = tk.Label(self.stats_frame, text="Location: ", background='grey', anchor='w', wraplength=180) # Wraplength based on frame width
        self.location_label.pack(anchor='w', fill='x', padx=5, pady=2)

        # Replace story_label with a Text widget for scrollable story text
        # self.story_label = tk.Label(self.story_frame, text='Story Goes Here', fg='white', bg='black')
        # self.story_label.pack(padx=10, pady=10)
        self.story_text_area = tk.Text(self.story_frame, state=tk.DISABLED, wrap=tk.WORD,
                                       bg='black', fg='white', relief=tk.FLAT,
                                       padx=5, pady=5) # Added relief and internal padding
        self.story_text_area.pack(expand=True, fill=tk.BOTH, padx=5, pady=5) # External padding for the widget itself

        # Replace input_label with an Entry widget and a Send button
        # self.input_label = tk.Label(self.input_frame, text='Input Goes Here', bg='darkgrey')
        # self.input_label.pack(padx=10, pady=10)

        # If game_manager is None (e.g. in test mode), button does nothing unless overridden later.
        cmd = None
        if self.game_manager and hasattr(self.game_manager, 'process_player_command'):
            cmd = self.game_manager.process_player_command

        quit_cmd = None
        if self.game_manager and hasattr(self.game_manager, 'quit_game'):
            quit_cmd = self.game_manager.quit_game

        # Pack order matters for side=tk.RIGHT. Last packed is furthest right.
        # So, pack Send button first if it should be on the far right.
        # Or, pack Quit button first if it should be on the far right, then Send to its left.
        # To have Quit on left of Send:
        # 1. Pack Send (tk.RIGHT)
        # 2. Pack Quit (tk.RIGHT) - this will put Quit to the left of Send.

        self.send_button = tk.Button(self.input_frame, text="Send", command=cmd)
        self.send_button.pack(side=tk.RIGHT, padx=(0, 5), pady=5) # No left padding for send if quit is next to it

        self.quit_button = tk.Button(self.input_frame, text="Save & Quit", command=quit_cmd)
        self.quit_button.pack(side=tk.RIGHT, padx=5, pady=5) # padx=(5,0) if send is on right

        self.input_entry = tk.Entry(self.input_frame, relief=tk.FLAT) # Added relief
        self.input_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

    def add_story_text(self, text: str):
        """
        Adds a line of text to the story text area.

        Args:
            text (str): The text to add.
        """
        self.story_text_area.config(state=tk.NORMAL)
        self.story_text_area.insert(tk.END, text + '\n')
        self.story_text_area.see(tk.END)
        self.story_text_area.config(state=tk.DISABLED)

    def get_player_input(self) -> str:
        """
        Retrieves the text from the input entry and clears the entry.

        Returns:
            str: The text entered by the player.
        """
        player_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        return player_input

    def update_player_display(self, player_object: Player):
        """
        Updates the player statistics display panel with the given player_object's data.
        """
        if not hasattr(self, 'name_label') or \
           not hasattr(self, 'hp_label') or \
           not hasattr(self, 'mp_label') or \
           not hasattr(self, 'location_label'):
            # Labels might not exist if UI setup failed or called too early.
            print("UI Warning: Player display labels not initialized yet.")
            return

        try:
            self.name_label.config(text=f"Name: {player_object.name}")
            self.hp_label.config(text=f"HP: {player_object.hp}/{player_object.max_hp}")
            self.mp_label.config(text=f"MP: {player_object.mp}/{player_object.max_mp}")
            self.location_label.config(text=f"Location: {player_object.current_location}")
        except Exception as e:
            print(f"Error updating player display: {e}")
            # Optionally, update labels to show an error state or partial info
            if hasattr(self, 'name_label'): self.name_label.config(text="Name: Error")
            if hasattr(self, 'hp_label'): self.hp_label.config(text="HP: Error")
            if hasattr(self, 'mp_label'): self.mp_label.config(text="MP: Error")
            if hasattr(self, 'location_label'): self.location_label.config(text="Location: Error")

    def start_ui(self):
        """
        Starts the tkinter main event loop.
        """
        self.root.mainloop()

if __name__ == '__main__':
    # This block is for testing the UI independently.
    # Note: For full functionality in this test block, game_manager_ref would need to be a mock
    # or a dummy object that has the methods GameUI might call on it (e.g., process_player_command).
    # Passing None here allows basic layout testing.
    root_window = tk.Tk()
    app_ui = GameUI(root_window, None) # Pass None for game_manager_ref for standalone testing

    # Example usage of add_story_text
    app_ui.add_story_text("Welcome to Mythic Realms!")
    app_ui.add_story_text("The wind howls outside the ancient ruins...")
    for i in range(20): # Add more lines to test scrolling
        app_ui.add_story_text(f"This is line number {i+3} in the story text area.")

    # Example usage of get_player_input (configuring the button)
    def handle_send_button_test_mode(): # Renamed to avoid conflict if game_manager had same method
        # In full operation, this would call game_manager.process_player_command()
        # For standalone UI testing, we simulate the input handling locally.
        user_text = app_ui.get_player_input()
        if user_text:
            app_ui.add_story_text(f"Test Mode > {user_text}")
            if app_ui.game_manager and hasattr(app_ui.game_manager, 'process_player_command'):
                # This part would only run if a mock/real game_manager with the method is passed
                app_ui.game_manager.process_player_command()
            else:
                app_ui.add_story_text("(No game manager to process command in test mode)")
        else:
            app_ui.add_story_text("Test Mode: You entered nothing.")

    app_ui.send_button.config(command=handle_send_button_test_mode)

    # Bind the Enter key to the send button's action (or the test mode handler)
    # The button's command is already set to handle_send_button_test_mode if running standalone.
    # If we want the Enter key to also use this test_mode handler:
    app_ui.input_entry.bind("<Return>", lambda event: handle_send_button_test_mode())
    # If the button's command was NOT overridden in test mode, and game_manager was None,
    # then the Enter key might also need a conditional command:
    # enter_cmd = app_ui.send_button.cget('command') # Get command set in __init__ or overridden
    # app_ui.input_entry.bind("<Return>", lambda event: enter_cmd() if enter_cmd else None)


    app_ui.start_ui() # Call the new method

import tkinter as tk
from tkinter import ttk # For themed widgets, if needed later

class GameUI:
    """
    Manages the main user interface for the Mythic Realms RPG.
    """
    def __init__(self, root):
        """
        Initializes the main game UI.

        Args:
            root: The root tkinter window.
        """
        self.root = root
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

        # Temporary labels for each frame
        self.stats_label = tk.Label(self.stats_frame, text='Stats Go Here', bg='grey')
        self.stats_label.pack(padx=10, pady=10)

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

        self.send_button = tk.Button(self.input_frame, text="Send")
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)

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

    def start_ui(self):
        """
        Starts the tkinter main event loop.
        """
        self.root.mainloop()

if __name__ == '__main__':
    # This block is for testing the UI independently.
    root_window = tk.Tk()
    app_ui = GameUI(root_window)

    # Example usage of add_story_text
    app_ui.add_story_text("Welcome to Mythic Realms!")
    app_ui.add_story_text("The wind howls outside the ancient ruins...")
    for i in range(20): # Add more lines to test scrolling
        app_ui.add_story_text(f"This is line number {i+3} in the story text area.")

    # Example usage of get_player_input (configuring the button)
    def handle_send_button():
        user_text = app_ui.get_player_input()
        if user_text: # Don't add empty lines
            app_ui.add_story_text(f"> {user_text}") # Display entered text in story area
        else:
            app_ui.add_story_text("You entered nothing.") # Or handle empty input differently

    app_ui.send_button.config(command=handle_send_button)
    
    # Bind the Enter key to the send button's action
    app_ui.input_entry.bind("<Return>", lambda event: handle_send_button())


    app_ui.start_ui() # Call the new method

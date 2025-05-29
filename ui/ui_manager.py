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

        self.story_label = tk.Label(self.story_frame, text='Story Goes Here', fg='white', bg='black')
        self.story_label.pack(padx=10, pady=10)

        self.input_label = tk.Label(self.input_frame, text='Input Goes Here', bg='darkgrey')
        self.input_label.pack(padx=10, pady=10)

    def start_ui(self):
        """
        Starts the tkinter main event loop.
        """
        self.root.mainloop()

if __name__ == '__main__':
    # This block is for testing the UI independently.
    root_window = tk.Tk()
    app_ui = GameUI(root_window)
    app_ui.start_ui() # Call the new method

from typing import List, Optional
from .common_types import AdventureLog

class Player:
    """
    Represents a player character in the game.
    """
    def __init__(self, player_id: int, name: str, hp: int, max_hp: int, mp: int, max_mp: int,
                 inventory: Optional[List[str]] = None, skills: Optional[List[str]] = None,
                 adventure_log: Optional[AdventureLog] = None): # Added adventure_log
        """
        Initializes a new Player instance.

        Args:
            player_id (int): The unique identifier for the player.
            name (str): The name of the player.
            hp (int): The current hit points of the player.
            max_hp (int): The maximum hit points of the player.
            mp (int): The current mana points of the player.
            max_mp (int): The maximum mana points of the player.
            inventory (Optional[List[str]], optional): The player's starting inventory.
                                                     Defaults to an empty list.
            skills (Optional[List[str]], optional): The player's skills.
                                                  Defaults to ["Meditate", "Power Attack"].
            adventure_log (Optional[AdventureLog], optional): The player's adventure log.
                                                            Defaults to a new AdventureLog instance.
        """
        self.player_id = player_id
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.mp = mp
        self.max_mp = max_mp
        self.inventory: List[str] = inventory if inventory is not None else []
        self.skills: List[str] = skills if skills is not None else ["Meditate", "Power Attack"]
        self.adventure_log: AdventureLog = adventure_log if adventure_log is not None else AdventureLog() # Initialize adventure_log
        self.current_location: str = 'Battlefield - Edge of the Kurukshetra' # Default, can be overwritten by load
        self.story_flags: dict = {} # Default, can be overwritten by load

    def __repr__(self):
        """
        Returns a string representation of the Player instance.
        """
        return (f"Player(player_id={self.player_id}, name='{self.name}', "
                f"hp={self.hp}/{self.max_hp}, mp={self.mp}/{self.max_mp}, "
                f"location='{self.current_location}', flags={self.story_flags}, "
                f"inventory={self.inventory}, skills={self.skills}, "
                f"adventure_log_entries={len(self.adventure_log.entries) if self.adventure_log else 0})") # Added adventure_log to repr

if __name__ == '__main__':
    # Example usage:
    # Player with default skills
    player1 = Player(player_id=1, name="Aragorn", hp=100, max_hp=100, mp=50, max_mp=50, inventory=["Sword", "Shield"])
    print(player1)
    print(f"  Player 1 Adventure Log Entries: {len(player1.adventure_log.entries)}")


    # Player with custom skills
    player2 = Player(player_id=2, name="Gandalf", hp=70, max_hp=80, mp=150, max_mp=150, skills=["Fireball", "Teleport"])
    print(player2)
    print(f"  Player 2 Adventure Log Entries: {len(player2.adventure_log.entries)}")

    # Player with default inventory and skills explicitly set to None (should use defaults)
    player3 = Player(player_id=3, name="Legolas", hp=90, max_hp=90, mp=70, max_mp=70, inventory=None, skills=None)
    print(player3)
    print(f"  Player 3 Adventure Log Entries: {len(player3.adventure_log.entries)}")


    # Player with empty list for skills
    player4 = Player(player_id=4, name="Gimli", hp=120, max_hp=120, mp=30, max_mp=30, skills=[])
    print(player4)
    print(f"  Player 4 Adventure Log Entries: {len(player4.adventure_log.entries)}")

class Player:
    """
    Represents a player character in the game.
    """
    def __init__(self, player_id: int, name: str, hp: int, max_hp: int, mp: int, max_mp: int):
        """
        Initializes a new Player instance.

        Args:
            player_id (int): The unique identifier for the player.
            name (str): The name of the player.
            hp (int): The current hit points of the player.
            max_hp (int): The maximum hit points of the player.
            mp (int): The current mana points of the player.
            max_mp (int): The maximum mana points of the player.
        """
        self.player_id = player_id
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.mp = mp
        self.max_mp = max_mp
        self.current_location: str = 'Battlefield - Edge of the Kurukshetra'
        self.story_flags: dict = {}

    def __repr__(self):
        """
        Returns a string representation of the Player instance.
        """
        return (f"Player(player_id={self.player_id}, name='{self.name}', "
                f"hp={self.hp}/{self.max_hp}, mp={self.mp}/{self.max_mp}, "
                f"location='{self.current_location}', flags={self.story_flags})")

if __name__ == '__main__':
    # Example usage:
    player1 = Player(player_id=1, name="Aragorn", hp=100, max_hp=100, mp=50, max_mp=50)
    print(player1)

    player2 = Player(player_id=2, name="Gandalf", hp=70, max_hp=80, mp=150, max_mp=150)
    print(player2)

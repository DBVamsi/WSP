from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class GameStateUpdates(BaseModel):
    inventory_add: List[str] = Field(default_factory=list)
    inventory_remove: List[str] = Field(default_factory=list)
    hp_change: int = 0
    mp_change: int = 0
    new_story_flags: Dict[str, bool] = Field(default_factory=dict)
    new_location: Optional[str] = None
    player_name: Optional[str] = None # New field
    # Future potential fields:
    # new_quests_added: List[str] = Field(default_factory=list)
    # quests_completed: List[str] = Field(default_factory=list)
    # npc_status_updates: Dict[str, str] = Field(default_factory=dict)

    class Config:
        # Allows to instantiate with extra fields from AI that are not defined here,
        # without raising an error. They will be ignored.
        extra = 'ignore'

if __name__ == '__main__':
    # Example usage and test
    updates_data_from_ai = {
        "inventory_add": ["sword of valor"],
        "inventory_remove": ["rusty dagger"],
        "hp_change": -10,
        "new_story_flags": {"met_king": True},
        "player_name": "HeroUpdated", # Test new field
        "some_other_field_from_ai": "will_be_ignored"
    }

    game_updates = GameStateUpdates(**updates_data_from_ai)

    print("Parsed GameStateUpdates:")
    print(f"  Inventory Add: {game_updates.inventory_add}")
    print(f"  Inventory Remove: {game_updates.inventory_remove}")
    print(f"  HP Change: {game_updates.hp_change}")
    print(f"  MP Change: {game_updates.mp_change}") # Will be default 0
    print(f"  New Story Flags: {game_updates.new_story_flags}")
    print(f"  New Location: {game_updates.new_location}") # Will be default None
    print(f"  Player Name: {game_updates.player_name}") # Test new field

    # Example of creating an empty update
    no_updates = GameStateUpdates()
    print("\nEmpty GameStateUpdates:")
    print(f"  Inventory Add: {no_updates.inventory_add}")
    print(f"  Player Name: {no_updates.player_name}") # Should be None

    # Example of AI returning fewer fields (player_name will be None)
    partial_updates_data = {
        "inventory_add": ["healing potion"],
        "hp_change": 20
    }
    partial_updates = GameStateUpdates(**partial_updates_data)
    print("\nPartial GameStateUpdates:")
    print(f"  Inventory Add: {partial_updates.inventory_add}")
    print(f"  HP Change: {partial_updates.hp_change}")
    print(f"  Inventory Remove: {partial_updates.inventory_remove}") # Default
    print(f"  Player Name: {partial_updates.player_name}") # Should be None

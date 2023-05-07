from dataclasses import dataclass

@dataclass
class Player:
    player_id: int
    created_by: str
    team_id: int
    first_name: str
    last_name: str
    position: str

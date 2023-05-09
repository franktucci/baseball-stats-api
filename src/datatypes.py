from dataclasses import dataclass

@dataclass
class Player:
    player_id: int
    created_by: str
    team_id: int
    first_name: str
    last_name: str
    position: str  # This will be a separate table in the near future!

@dataclass
class Game:
    game_id: int
    created_by: str
    home_team_id: int
    away_team_id: str
    home_score: str
    away_score: str

@dataclass
class Event:
    event_id: int
    game_id: int
    player_id: int
    inning: int
    BT: int
    enum: int

@dataclass
class Team:
    team_id: int
    created_by: str
    team_city: str
    team_name: str

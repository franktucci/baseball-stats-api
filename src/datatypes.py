from dataclasses import dataclass

@dataclass
class Player:
    player_id: int
    created_by: str
    team_id: int
    first_name: str
    last_name: str
    position: str

@dataclass
class Game:
    game_id: int
    created_by: str
    home_score: str
    away_score: str
    home_team_id: int
    away_team_id: int

@dataclass
class Event:
    event_id: int
    inning: int
    game_id: int
    enum: int
    player_id: int
    BT: int

@dataclass
class Team:
    team_id: int
    created_by: str
    team_city: str
    team_name: str

@dataclass
class User:
    username: str
    password_hash: str

@dataclass
class EventEnum:
    enum: int
    string: str

@dataclass
class PlayerStats:
    player_id: int
    single_count: int
    double_count: int
    triple_count: int
    hr_count: int
    walk_count: int
    strike_out_count: int
    hit_by_pitch_count: int
    sac_fly_count: int
    other_out_count: int

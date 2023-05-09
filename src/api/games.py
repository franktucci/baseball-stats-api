from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query
from sqlalchemy import create_engine
import os
import dotenv
import sqlalchemy
import dotenv
from pydantic import BaseModel
from typing import List

router = APIRouter()

class LineupJson(BaseModel):
    team_id: int
    lineup: List[int]
class GameJson(BaseModel):
    lineup1: LineupJson
    lineup2: LineupJson

class EventCodes(Enum):
    SINGLE = 0
    DOUBLE = 1
    TRIPLE = 2
    HR = 3
    WALK = 4
    STRIKE_OUT = 5
    HIT_PITCH = 6
    SAC_FLY = 7
    OTHER_OUT = 8
    STOLEN = 9
    CAUGHT_STEALING = 10



@router.get("/games/{game_id}", tags=["games"])
def get_game(game_id: int):
    """
    This endpoint returns a game in 2022. It returns:
    * `game_id`: The internal id of the team. Can be used to query the
      `/games/{game_id}` endpoint.
    * `created_by`: The user who created the team. Is null for real-life games.
    * `home_team`: The id of the home team.
    * `away_name`: The id of the team.
    * `home_score`: The score of the home team.
    * `away_score`: The score of the away team.
    """

    stmt = (
        sqlalchemy.select(
            db.games.c.game_id,
            db.games.c.created_by,
            db.games.c.home_team_id,
            db.games.c.away_team_id,
            db.games.c.home_score,
            db.games.c.away_score
        )
        .where(db.games.c.game_id == game_id)
    )
    with db.engine.connect() as conn:
        games_result = conn.execute(stmt)

    game = games_result.first()

    if game is None:
        raise HTTPException(status_code=404, detail="game not found.")

    return {
        "game_id": game.game_id,
        "created_by": game.created_by,
        "home_team_id": game.home_team_id,  # change these to name in the future
        "away_team_id": game.away_team_id,
        "home_score": game.home_score,
        "away_score": game.away_score
    }

@router.post("/games/", tags=["games"])
def simulate(game: GameJson):
    """
    This endpoint takes in two lineup objects and returns a simulated game object. A lineup consists of:
    * `team_id`: The internal id of the team. Can be used to query the `/view_roster/{team_id}` endpoint.
    * `lineup`: A list of exactly 10 player_ids (0 is the designated hitter, 1-9 are in batting order).

    This endpoint returns a game object. This game object calculates a random game based on a player’s given stats. This consists of:
    * `winner`: The team id of the winning team.
    * `loser`: The team id of the losing team.
    * `score`: The ending score of the game.
    * `play_by_play`: A list of event objects that occurred in the game.

    Each event is represented by a dictionary with the following keys:
    * `inning`: The inning of the game.
    * `T/B` Top/Bottom of inning.
    * `player`: Player name of batter.
    * `happening`: What the player did. Some examples include Walk, Strikeout, Home Run, etc.
    """
    if len(game.lineup1.lineup) != 10 or len(game.lineup2.lineup) != 10:
        raise HTTPException(status_code=422, detail="Endpoint was not given 10 players.")
    if game.lineup1.team_id == game.lineup2.team_id:
        raise HTTPException(status_code=422, detail="Team cannot play itself.")
    for team in [game.lineup1, game.lineup2]:
        for player in team.lineup:
            if team.lineup.count(player) > 1:
                raise HTTPException(status_code=422, detail="Team contains duplicate players.")

    return {}

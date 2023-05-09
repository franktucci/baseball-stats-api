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

@router.get("/players/{player_id}", tags=["players"])
def get_player(player_id: int):
    """
    This endpoint returns a player's stats for 2022.

    * `player_id`: The internal id of the player. Can be used to query the
      `/players/{player_id}` endpoint.
    * `player_name`: The name of the player.
    * `created_by`: The user who created the team. Is null for real-life teams.
    * `team_id`: The internal id of the team the player plays on. Can be used to query the
      `/teams/{team_id}` endpoint.
    * `positions`: A string representation of the positions a character can play.
    * `at_bat`: The number of times a player has been up to bat, total.
    * `singles`: The number of times the ball is hit and the batter gets to first base.
    * `doubles`: The number of times the ball is hit and grants the batter 2 bases.
    * `triples`: The number of times the ball is hit and grants the batter 3 bases.
    * `home_runs`: The number of times the batter hits a home run.
    * `walks`: The number of times the batter walks. This grants the batter one base.
    * `strike_outs`: The number of times the batter strikes out.
    * `hit_by_pitch`: The number of times the batter is hit by the pitch. This grants the batter one base.
    * `sacrifice_flies`: The number of times the batter hits a fly ball that is caught out with less than two outs and, in the process, assists in a run.
    * `stolen_bases`: The number of times a runner successfully has stolen a base.
    * `caught_stealing`: The number of times a runner gets out in the process of stealing a base.
    * `on_base_percent`: Calculated (Hit + Ball + HBP) / (At-Bat + Walk + HBP + Sacrifice-Fly)
    * `batting_average`: Calculated Hit / At-bat

    You can filter for players whose name contains a string by using the
    `name` or created by using the `created_by` query parameters, as well as real=True for only real teams, or team={team_id} for a specific team.
    """

    stmt = (
        sqlalchemy.select(
            db.players.c.player_id,
            db.players.c.first_name,
            db.players.c.last_name,
            db.players.c.team_id,
            db.players.c.created_by,
            db.players.c.position
        )
        .where(db.players.c.player_id == player_id)
    )
    with db.engine.connect() as conn:
        players_result = conn.execute(stmt)

    player = players_result.first()

    if player is None:
         raise HTTPException(status_code=404, detail="player not found.")

    stmt = (
        sqlalchemy.select(
            db.events.c.enum,
            sqlalchemy.func.count()
        )
        .where(db.events.c.player_id == player_id)
        .group_by(db.events.c.enum)
    )
    with db.engine.connect() as conn:
        events_result = conn.execute(stmt)

    events = {}

    for row in events_result:
        events[row[0]] = row[1]

    singles = events.get(EventCodes.SINGLE.value) or 0
    doubles = events.get(EventCodes.DOUBLE.value) or 0
    triples = events.get(EventCodes.TRIPLE.value) or 0
    hrs = events.get(EventCodes.HR.value) or 0
    walks = events.get(EventCodes.WALK.value) or 0
    strike_outs = events.get(EventCodes.STRIKE_OUT.value) or 0
    hit_bys = events.get(EventCodes.HIT_PITCH.value) or 0
    sac_flies = events.get(EventCodes.SAC_FLY.value) or 0
    other_outs = events.get(EventCodes.OTHER_OUT.value) or 0
    stolen = events.get(EventCodes.STOLEN.value) or 0
    caught_stealing = events.get(EventCodes.CAUGHT_STEALING.value) or 0
    hits = singles + doubles + triples + hrs
    at_bats = hits + walks + strike_outs + hit_bys + sac_flies + other_outs

    return {
        'player_id': player_id,
        'player_name': player.first_name + " " + player.last_name,
        'positions': player.position,
        'at_bat': at_bats,
        'singles': singles,
        'doubles': doubles,
        'home_runs': hrs,
        'walks': walks,
        'strike_outs': strike_outs,
        'hit_by_pitch': hit_bys,
        'sacrifice_flies': sac_flies,
        'stolen_bases': stolen,
        'caught_stealing': caught_stealing,
        'on_base_percent': 0.0 if (at_bats + walks + hit_bys + sac_flies) == 0 else round((hits + walks + hit_bys) / (at_bats + walks + hit_bys + sac_flies), 3),
        'batting_average': 0.0 if at_bats == 0 else round(hits / at_bats, 3)
    }

class PlayerJson(BaseModel):
    first_name: str
    last_name: str
    team_id: int
    created_by: str
    position: str

@router.post("/players/", tags=["players"])
def add_player(player: PlayerJson):
    if player.created_by is None:
        raise HTTPException(status_code=422, detail="must specify a player creator.")

    stmt = (
        sqlalchemy.select(
            db.teams.c.team_id,
        )
        .where(db.teams.c.team_id == player.team_id)
    )
    with db.engine.connect() as conn:
        team_result = conn.execute(stmt)

    if team_result.first() is None:
        raise HTTPException(status_code=422, detail="team must exist.")

    stmt = (sqlalchemy.select(db.players.c.player_id).order_by(sqlalchemy.desc('player_id')))

    with db.engine.connect() as conn:
        player_result = conn.execute(stmt)

    player_id = player_result.first().player_id + 1

    with db.engine.begin() as conn:
        conn.execute(
            db.players.insert().values(
                player_id=player_id,
                created_by=player.created_by,
                team_id=player.team_id,
                first_name=player.first_name,
                last_name=player.last_name,
                position=player.position
            )
        )
    return {'player_id': player_id}

class players_sort_options(str, Enum):
    player_name = "first_name"
    # team
    # obp
    # avg

# # Add get parameters
# @router.get("/players/", tags=["players"])
# def list_players(
#     name: str = "",
#     limit: int = Query(50, ge=1, le=250),
#     offset: int = Query(0, ge=0),
#     sort: players_sort_options = players_sort_options.player_name,
# ):
#     """
#     This endpoint returns a list of players in 2022. For each player it returns:
#
#     * `player_id`: The internal id of the player. Can be used to query the
#       `/players/{player_id}` endpoint.
#     * `player_name`: The name of the player.
#     * `created_by`: The user who created the team. Is null for real-life teams.
#     * `positions`: A list of position_ids that the player is able to play.
#     * `at_bat`: The number of times a player has been up to bat, total.
#     * `runs`: The number of runs scored by the player.
#     * `hits`: The number of times the ball is hit and the batter gets to at least first base.
#     * `doubles`: The number of times the ball is hit and grants the batter 2 bases.
#     * `triples`: The number of times the ball is hit and grants the batter 3 bases.
#     * `home_runs`: The number of times the batter hits a home run.
#     * `walks`: The number of times the batter walks. This grants the batter one base.
#     * `strike_outs`: The number of times the batter strikes out.
#     * `hit_by_pitch`: The number of times the batter is hit by the pitch. This grants the batter one base.
#     * `sacrifice_flies`: The number of times the batter hits a fly ball that is caught out with less than two outs and, in the process, assists in a run.
#     * `stolen_bases`: The number of times a runner successfully has stolen a base.
#     * `caught_stealing`: The number of times a runner gets out in the process of stealing a base.
#     * `on_base_percent`: Calculated (Hit + Ball + HBP) / (At-Bat + Walk + HBP + Sacrifice-Fly)
#     * `batting_average`: Calculated Hit / At-bat
#     """
#
#     if sort is players_sort_options.player_name:
#         order_by = db.players.c.first_name
#     else:
#         assert False
#
#     stmt = (
#         sqlalchemy.select(
#             db.players.c.player_id,
#             db.players.c.player_name
#         )
#         .limit(limit)
#         .offset(offset)
#         .order_by(order_by, db.players.c.player_id)
#     )
#
#     # filter only if name parameter is passed
#     if name != "":
#         stmt = stmt.where(db.players.c.player_name.ilike(f"%{name}%"))
#
#     with db.engine.connect() as conn:
#         result = conn.execute(stmt)
#         json = []
#         for row in result:
#             json.append(
#                 {
#                     'player_id': row.player_id,
#                     'player_name': row.first_name + " " + row.last_name
#                 }
#             )
#
#     return json

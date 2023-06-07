from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query
from sqlalchemy import create_engine
import os
import dotenv
import sqlalchemy
from pydantic import BaseModel
from typing import List
import random
from Crypto.Hash import SHA256

router = APIRouter()

def calculate_hits(row):
    return row.single_count + row.double_count + row.triple_count + row.hr_count
def calculate_at_bats(row):
    return calculate_hits(row) + row.walk_count + row.strike_out_count + row.hit_by_pitch_count + row.sac_fly_count + row.other_out_count
def filter_helper(e):
    return sqlalchemy.funcfilter(sqlalchemy.func.count(db.events.c.enum), sqlalchemy.and_((db.events.c.enum == e.value), sqlalchemy.or_(db.events.c.player_id > 1682, sqlalchemy.and_((db.events.c.player_id <= 1682), (db.events.c.game_id <= 2429))))).label(e.name.lower() + '_count')

class EventCodes(Enum):
    SINGLE = 0
    DOUBLE = 1
    TRIPLE = 2
    HR = 3
    WALK = 4
    STRIKE_OUT = 5
    HIT_BY_PITCH = 6
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
    * `home_team_id`: The id of the home team. Can be used to query the `/teams/{team_id}` endpoint.
    * `away_team_id`: The id of the away team. Can be used to query the `/teams/{team_id}` endpoint.
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
        "home_team_id": game.home_team_id,
        "away_team_id": game.away_team_id,
        "home_score": game.home_score,
        "away_score": game.away_score
    }


def simulate_inning(inning, player_stats, lineups, orders):
    half = 0
    inn_events = []
    inn_runs_home = 0
    inn_runs_away = 0
    inn_order_home = orders[0]
    inn_order_away = orders[1]

    while half < 2:
        half_events, half_runs, batting_order = simulate_half(inning, half, player_stats, lineups[half], orders[half])
        [inn_events.append(event) for event in half_events]
        if half == 0:
            inn_runs_home += half_runs
            inn_order_home = batting_order
        else:
            inn_runs_away += half_runs
            inn_order_away = batting_order
        half += 1
    return inn_events, inn_runs_home, inn_runs_away, inn_order_home, inn_order_away

def simulate_half(inning, half, player_stats, lineup, order):
    outs = 0
    half_events = []
    bases = [False, False, False]
    half_runs = 0

    while outs < 3:
        if order > 9:
            order = 1
        event, out, runs = simulate_event(inning, half, player_stats[lineup[order]], bases)
        half_events.append(event)
        outs += out
        half_runs += runs
        order += 1
    return half_events, half_runs, order

def simulate_event(inning, half, player, bases):
    runs = 0
    outs = 0
    at_bats = calculate_at_bats(player)

    if at_bats < 5:
        single_prp = .20
        double_prp = single_prp + .05
        triple_prp = double_prp + .01
        hr_prp = triple_prp + .01
        walk_prp = hr_prp + .10
        strike_out_prp = walk_prp + .50
        hit_by_prp = strike_out_prp + .01
        sac_fly_prp = hit_by_prp + .05
        other_prp = 1
    else:
        single_prp = player.single_count / at_bats
        double_prp = single_prp + (player.double_count / at_bats)
        triple_prp = double_prp + (player.triple_count / at_bats)
        hr_prp = triple_prp + (player.hr_count / at_bats)
        walk_prp = hr_prp + (player.walk_count / at_bats)
        strike_out_prp = walk_prp + (player.strike_out_count / at_bats)
        hit_by_prp = strike_out_prp + (player.hit_by_pitch_count / at_bats)
        sac_fly_prp = hit_by_prp + (player.sac_fly_count / at_bats)
        other_prp = 1

    rand = random.random()
    if (0 <= rand < single_prp) or (hr_prp <= rand < walk_prp) or (strike_out_prp <= rand < hit_by_prp):
        if 0 <= rand < single_prp:
            event_code = EventCodes.SINGLE.value
        elif hr_prp <= rand < walk_prp:
            event_code = EventCodes.WALK.value
        else:
            event_code = EventCodes.HIT_BY_PITCH.value
        bases.insert(0, True)
        if bases.pop():
            runs += 1
    elif single_prp <= rand < double_prp:
        event_code = EventCodes.DOUBLE.value
        bases.insert(0, True)
        bases.insert(0, False)
        if bases.pop():
            runs += 1
        if bases.pop():
            runs += 1
    elif double_prp <= rand < triple_prp:
        event_code = EventCodes.TRIPLE.value
        bases.insert(0, True)
        bases.insert(0, False)
        bases.insert(0, False)
        if bases.pop():
            runs += 1
        if bases.pop():
            runs += 1
        if bases.pop():
            runs += 1
    elif triple_prp <= rand < hr_prp:
        event_code = EventCodes.HR.value
        bases.insert(0, True)
        bases.insert(0, False)
        bases.insert(0, False)
        bases.insert(0, False)
        if bases.pop():
            runs += 1
        if bases.pop():
            runs += 1
        if bases.pop():
            runs += 1
        if bases.pop():
            runs += 1
    else:
        if walk_prp <= rand < strike_out_prp:
            event_code = EventCodes.STRIKE_OUT.value
        elif hit_by_prp <= rand < sac_fly_prp:
            event_code = EventCodes.SAC_FLY.value
        else:
            event_code = EventCodes.OTHER_OUT.value
        outs += 1

    event = {
            'player_id': player.player_id,
            'inning': inning,
            'B/T': half,
            'enum': event_code
        }
    return event, outs, runs

class LineupJson(BaseModel):
    team_id: int
    lineup: List[int]

class GameJson(BaseModel):
    created_by: str
    password: str
    lineup1: LineupJson
    lineup2: LineupJson

@router.post("/games/", tags=["games"])
def simulate(game: GameJson):
    """
    This endpoint takes in `created by`, `password`, and two lineup objects. A lineup consists of:
    * `team_id`: The internal id of the team. Can be used to query the `/teams/{team_id}` endpoint.
    * `lineup`: A list of exactly 10 player_ids (0 is the designated hitter, 1-9 are in batting order).

    This endpoint returns a simulated game object. This game object calculates a random game based on a
    player’s given stats. This consists of:
    * `game_id`: The game id.
    * `home_score`: The final score of the home team.
    * `away_score`: The final score of the away team.
    * `events`: A list of event objects that occurred in the game.

    Each event is represented by a dictionary with the following keys:
    * `inning`: The inning of the game.
    * `T/B` Top/Bottom of inning.
    * `player`: Player name of batter.
    * `happening`: What the player did. Some examples include Walk, Strikeout, Home Run, etc.
    """

    if game.created_by is None:
        raise HTTPException(status_code=422, detail="must specify a username.")

    stmt = (
        sqlalchemy.select(
            db.users.c.username,
            db.users.c.password_hash
        )
        .where(db.users.c.username == game.created_by)
    )

    with db.engine.connect() as conn:
        user_result = conn.execute(stmt)

    user = user_result.first()
    if user is None:
        raise HTTPException(status_code=422, detail="user is not registered. Register at /users/.")

    d = SHA256.new()
    d.update(bytes(game.password, 'utf8'))
    if d.hexdigest() != user.password_hash:
        raise HTTPException(status_code=422, detail="incorrect password.")

    if len(game.lineup1.lineup) != 10 or len(game.lineup2.lineup) != 10:
        raise HTTPException(status_code=422, detail="please give 10 players from each team per team lineup.")
    if game.lineup1.team_id == game.lineup2.team_id:
        raise HTTPException(status_code=422, detail="team cannot play itself!.")

    for team in [game.lineup1, game.lineup2]:
        for player in team.lineup:
            if game.lineup1.lineup.count(player) + game.lineup2.lineup.count(player) > 1:
                raise HTTPException(status_code=422, detail="game contains duplicate players.")

    stmt = (
        sqlalchemy.select(
            db.players.c.player_id,
            filter_helper(EventCodes.SINGLE),
            filter_helper(EventCodes.DOUBLE),
            filter_helper(EventCodes.TRIPLE),
            filter_helper(EventCodes.HR),
            filter_helper(EventCodes.WALK),
            filter_helper(EventCodes.STRIKE_OUT),
            filter_helper(EventCodes.HIT_BY_PITCH),
            filter_helper(EventCodes.SAC_FLY),
            filter_helper(EventCodes.OTHER_OUT),
            filter_helper(EventCodes.STOLEN),
            filter_helper(EventCodes.CAUGHT_STEALING),
        )
        .select_from(db.players.join(db.events, db.events.c.player_id == db.players.c.player_id, isouter=True))
        .where(db.players.c.player_id.in_(game.lineup1.lineup) | db.players.c.player_id.in_(game.lineup2.lineup))
        .group_by(db.players.c.player_id, db.events.c.enum)
    )

    with db.engine.connect() as conn:
        events_result = conn.execute(stmt)

    player_stats = {
        player.player_id: player
        for player in events_result
    }

    if len(player_stats) < 20:
        raise HTTPException(status_code=422, detail="player not found.")

    inning = 1
    home_score = 0
    away_score = 0
    events = []
    lineups = [game.lineup1.lineup, game.lineup2.lineup]
    orders = [1, 1]

    while inning < 10:
        inn_events, inn_runs_home, inn_runs_away, inn_order_home, inn_order_away = simulate_inning(inning, player_stats, lineups, orders)
        [events.append(event) for event in inn_events]
        home_score += inn_runs_home
        away_score += inn_runs_away
        orders = [inn_order_away, inn_order_away]
        inning += 1

    events_output = []

    with db.engine.begin() as conn:
        games_result = conn.execute(
            db.games.insert().values(
                created_by=game.created_by,
                home_team_id=game.lineup1.team_id,
                away_team_id=game.lineup2.team_id,
                home_score=home_score,
                away_score=away_score
            ).returning(db.games.c.game_id)
        )
        game_id = games_result.first().game_id
        for event in events:
            events_output.append(
                {
                    'game_id': game_id,
                    'player_id': event['player_id'],
                    'inning': event['inning'],
                    'BT': event['B/T'],
                    'enum': event['enum']
                }
            )
        conn.execute(db.events.insert(), events_output)

    stmt = (
        sqlalchemy.select(
            db.events.c.inning,
            db.events.c.BT,
            db.players.c.first_name,
            db.players.c.last_name,
            db.event_enums.c.string
        )
        .select_from(db.events.join(db.players, db.events.c.player_id == db.players.c.player_id).join(db.event_enums, db.events.c.enum == db.event_enums.c.enum))
        .where(db.events.c.game_id == game_id)
    )
    with db.engine.connect() as conn:
        events_result = conn.execute(stmt)

    events = []

    for event in events_result:
        events.append(
            {
                'inning': event.inning,
                'T/B': event.BT,
                'player': event.first_name + " " + event.last_name,
                'happening': event.string
            }
        )
    return {
        'game_id': game_id,
        'home_score': home_score,
        'away_score': away_score,
        'events': events
    }

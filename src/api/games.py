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
import random

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

@router.get("/games/{game_id}", tags=["games"])
def get_game(game_id: int):
    """
    This endpoint returns a game in 2022. It returns:
    * `game_id`: The internal id of the team. Can be used to query the
      `/games/{game_id}` endpoint.
    * `created_by`: The user who created the team. Is null for real-life games.
    * `home_team`: The name of the home team.
    * `home_team_id`: The id of the home team. Can be used to query the `/teams/{team_id}` endpoint.
    * `away_team`: The name of the away team.
    * `away_team_id`: The id of the away team. Can be used to query the `/teams/{team_id}` endpoint.
    * `home_score`: The score of the home team.
    * `away_score`: The score of the away team.
    * `events`: A list of events during the game.

    Each event is represented by a dictionary with the following keys:
    * `event_id`: the internal id of the event.
    * `inning`: The inning.
    * `T/B`: 0 for top, 1 for bottom.
    * `player_id`: The player id. Can be used to query the `/players/{player_id}` endpoint.
    * `happening`: What the player did.
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

class LineupJson(BaseModel):
    team_id: int
    lineup: List[int]
class GameJson(BaseModel):
    created_by: str
    lineup1: LineupJson
    lineup2: LineupJson

def simulate_innings(inning: int):
        while inning < 10:
            BT=0
            home_bat_order = 1
            away_bat_order = 1
            simulate_BTs(BT)
            BT+=1
            inning+=1

def simulate_BTs(BT: int):
    while BT < 2:
        outs = 0
        bases = [False, False, False]
        simulate_outs(outs)
        BT+=1

def simulate_outs(outs: int):
    while outs < 3:
            bat_order = home_bat_order if BT == 0 else away_bat_order
            lineup = game.lineup1.lineup if BT == 0 else game.lineup2.lineup

def simulate_at_bat():
    # input: batter, strikes, walks
    # ouput: get a strike, get a walk, get on base, get
    # half_of_inning:
        # state of field whose on base
    half_of_inning=0

@router.post("/games/", tags=["games"])
def simulate(game: GameJson):
    """
    This endpoint takes in `created by` and two lineup objects and returns a simulated game object. A lineup consists of:
    * `team_id`: The internal id of the team. Can be used to query the `/view_roster/{team_id}` endpoint.
    * `lineup`: A list of exactly 10 player_ids (0 is the designated hitter, 1-9 are in batting order).

    This endpoint returns a game object. This game object calculates a random game based on a player’s given stats. This consists of:
    * `game_id`: The game id.
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

    stmt = (
        sqlalchemy.select(
            db.events.c.player_id,
            db.events.c.enum,
            sqlalchemy.func.count()
        )
        .where(db.events.c.player_id.in_(game.lineup1.lineup) | db.events.c.player_id.in_(game.lineup2.lineup))
        .group_by(db.events.c.player_id, db.events.c.enum)
    )

    with db.engine.connect() as conn:
        events_result = conn.execute(stmt)

    stats = {}

    for row in events_result:
        if stats.get(row[0]) is None:
            stats[row[0]] = {row[1]: row[2]}
        else:
            stats[row[0]][row[1]] = row[2]

    stmt = (sqlalchemy.select(db.games.c.game_id).order_by(sqlalchemy.desc('game_id')))
    with db.engine.connect() as conn:
        game_result = conn.execute(stmt)
    game_id = game_result.first().game_id + 1

    stmt = (sqlalchemy.select(db.events.c.event_id).order_by(sqlalchemy.desc('event_id')))
    with db.engine.connect() as conn:
        event_result = conn.execute(stmt)
    event_id = event_result.first().event_id + 1

    events = []

    inning = 1
    home_score = 0
    away_score = 0
    while inning < 10:
        BT = 0
        home_bat_order = 1
        away_bat_order = 1
        while BT < 2:
            outs = 0
            bases = [False, False, False]
            while outs < 3:
                bat_order = home_bat_order if BT == 0 else away_bat_order
                lineup = game.lineup1.lineup if BT == 0 else game.lineup2.lineup

                if stats.get(lineup[bat_order]) is None:
                    stats[lineup[bat_order]] = {}

                singles = stats[lineup[bat_order]].get(EventCodes.SINGLE.value) or 0
                doubles = stats[lineup[bat_order]].get(EventCodes.DOUBLE.value) or 0
                triples = stats[lineup[bat_order]].get(EventCodes.TRIPLE.value) or 0
                hrs = stats[lineup[bat_order]].get(EventCodes.HR.value) or 0
                walks = stats[lineup[bat_order]].get(EventCodes.WALK.value) or 0
                strike_outs = stats[lineup[bat_order]].get(EventCodes.STRIKE_OUT.value) or 0
                hit_bys = stats[lineup[bat_order]].get(EventCodes.HIT_PITCH.value) or 0
                sac_flies = stats[lineup[bat_order]].get(EventCodes.SAC_FLY.value) or 0
                other_outs = stats[lineup[bat_order]].get(EventCodes.OTHER_OUT.value) or 0

                # We'll use these later
                stolen = stats[lineup[bat_order]].get(EventCodes.STOLEN.value) or 0
                caught_stealing = stats[lineup[bat_order]].get(EventCodes.CAUGHT_STEALING.value) or 0

                hits = singles + doubles + triples + hrs
                at_bats = hits + walks + strike_outs + hit_bys + sac_flies + other_outs

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
                    single_prp = singles / at_bats
                    double_prp = single_prp + (doubles / at_bats)
                    triple_prp = double_prp + (triples / at_bats)
                    hr_prp = triple_prp + (hrs / at_bats)
                    walk_prp = hr_prp + (walks / at_bats)
                    strike_out_prp = walk_prp + (strike_outs / at_bats)
                    hit_by_prp = strike_out_prp + (hit_bys / at_bats)
                    sac_fly_prp = hit_by_prp + (sac_flies / at_bats)
                    other_prp = 1

                rand = random.random()
                if (0 <= rand < single_prp) or (hr_prp <= rand < walk_prp) or (strike_out_prp <= rand < hit_by_prp):
                    if 0 <= rand < single_prp:
                        event_code = EventCodes.SINGLE.value
                    elif hr_prp <= rand < walk_prp:
                        event_code = EventCodes.WALK.value
                    else:
                        event_code = EventCodes.HIT_PITCH.value
                    bases.insert(0, True)
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                elif single_prp <= rand < double_prp:
                    event_code = EventCodes.DOUBLE.value
                    bases.insert(0, True)
                    bases.insert(0, False)
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                elif double_prp <= rand < triple_prp:
                    event_code = EventCodes.TRIPLE.value
                    bases.insert(0, True)
                    bases.insert(0, False)
                    bases.insert(0, False)
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                elif triple_prp <= rand < hr_prp:
                    event_code = EventCodes.HR.value
                    bases.insert(0, True)
                    bases.insert(0, False)
                    bases.insert(0, False)
                    bases.insert(0, False)
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                    if bases.pop():
                        if BT == 0:
                            home_score += 1
                        else:
                            away_score += 1
                else:
                    if walk_prp <= rand < strike_out_prp:
                        event_code = EventCodes.SINGLE.value
                    elif hit_by_prp <= rand < sac_fly_prp:
                        event_code = EventCodes.WALK.value
                    else:
                        event_code = EventCodes.OTHER_OUT.value
                    outs += 1
                events.append(
                    {
                        'event_id': event_id,
                        'game_id': game_id,
                        'player_id': lineup[bat_order],
                        'inning': inning,
                        'B/T': BT,
                        'enum': event_code
                    }
                )
                event_id += 1
                if BT == 0:
                    home_bat_order += 1
                    if home_bat_order > 9:
                        home_bat_order = 1
                else:
                    away_bat_order += 1
                    if away_bat_order > 9:
                        away_bat_order = 1
            BT += 1
        inning += 1
    with db.engine.begin() as conn:
        conn.execute(
            db.games.insert().values(
                game_id=game_id,
                created_by=game.created_by,
                home_team_id=game.lineup1.team_id,
                away_team_id=game.lineup2.team_id,
                home_score=home_score,
                away_score=away_score
            )
        )
        for event in events:
            conn.execute(
                db.events.insert().values(
                    event_id=event['event_id'],
                    game_id=game_id,
                    player_id=event['player_id'],
                    inning=event['inning'],
                    BT=event['B/T'],
                    enum=event['enum']
                )
            )
    return {'game_id': game_id}

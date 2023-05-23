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
from Crypto.Hash import SHA256

router = APIRouter()


@router.get("/teams/{team_id}", tags=["teams"])
def get_team(team_id: int):
    """
    This endpoint returns a team's information in 2022. It returns:
    * `team_id`: The internal id of the team. Can be used to query the
      `/teams/{team_id}` endpoint.
    * `created_by`: The user who created the team. Is null for real-life teams.
    * `team_city`: The city the team is located in. Can be null for virtual teams.
    * `team_name`: The name of the team.
    * `players`: A list of the team's player_id's. Can be used to query the
      `/players/{player_id}` endpoint.
    """

    stmt = (
        sqlalchemy.select(
            db.teams.c.team_id,
            db.teams.c.created_by,
            db.teams.c.team_city,
            db.teams.c.team_name,
        )
        .where(db.teams.c.team_id == team_id)
    )
    with db.engine.connect() as conn:
        teams_result = conn.execute(stmt)

    team = teams_result.first()

    if team is None:
         raise HTTPException(status_code=404, detail="team not found.")

    stmt = (
        sqlalchemy.select(
            db.players.c.player_id
        )
        .where(db.players.c.team_id == team_id)
    )
    with db.engine.connect() as conn:
        players_result = conn.execute(stmt)

    players = []

    for row in players_result:
        players.append(row[0])

    return {
        "team_id": team.team_id,
        "created_by": team.created_by,
        "team_city": team.team_city,
        "team_name": team.team_name,
        "players": players
    }

class team_sort_options(str, Enum):
    team_name = "team_name"
    team_id = "team_id"

class TeamJson(BaseModel):
    team_city: str
    team_name: str
    created_by: str
    password: str

@router.post("/teams/", tags=["teams"])
def add_team(team: TeamJson):
    """
    This endpoint takes in a `team_name`, `team_city`, `created_by`, and `password`.

    The endpoint returns the id of the resulting team that was created.
    """

    if team.created_by is None:
        raise HTTPException(status_code=422, detail="must specify a username.")

    stmt = (
        sqlalchemy.select(
            db.users.c.username,
            db.users.c.password_hash
        )
        .where(db.users.c.username == team.created_by)
    )

    with db.engine.connect() as conn:
        user_result = conn.execute(stmt)

    user = user_result.first()
    if user is None:
        raise HTTPException(status_code=422, detail="user is not registered. Register at /users/.")

    d = SHA256.new()
    d.update(bytes(team.password, 'utf8'))
    if d.hexdigest() != user.password_hash:
        raise HTTPException(status_code=422, detail="incorrect password.")

    stmt = (sqlalchemy.select(db.teams.c.team_id).order_by(sqlalchemy.desc('team_id')))

    with db.engine.connect() as conn:
        team_result = conn.execute(stmt)

    team_id = team_result.first().team_id + 1

    with db.engine.begin() as conn:
        conn.execute(
            db.teams.insert().values(
                team_id=team_id,
                created_by=team.created_by,
                team_city=team.team_city,
                team_name=team.team_name
            )
        )
    return {'team_id': team_id}

# Add get parameters
@router.get("/teams/", tags=["teams"])
def list_teams(
    name: str = "",
    created: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: team_sort_options = team_sort_options.team_name,
):
    """
    This endpoint returns a list of teams. For each team it returns:

    * `team_id`: The internal id of the team. Can be used to query the /teams/{team_id} endpoint.
    * `created_by`: The user who created the team. Is null for real-life teams.
    * `team_city`: The city the team is located in. Can be null for fictional teams.
    * `team_name`: The name of the team.
    * You can filter for teams whose name contains a string by using the name or created by by using the
    `name` and/or `created` query parameters.

    You can sort the results by using the `sort` query parameter:
    * `id` - Sort by team_id.
    * `name` - Sort by team name alphabetically.
    """

    if sort is team_sort_options.team_name:
        order_by = db.teams.c.team_name
    else:
        order_by = db.teams.c.team_id

    stmt = (
        sqlalchemy.select(
            db.teams.c.team_id,
            db.teams.c.created_by,
            db.teams.c.team_city,
            db.teams.c.team_name,
        )
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.teams.c.team_id)
    )

    if name != "":
        stmt = stmt.where(db.teams.c.team_name.ilike(f"%{name}%"))
    if created != "":
        stmt = stmt.where(db.teams.c.created_by.ilike(f"%{created}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "team_id": row.team_id,
                    "created_by": row.created_by,
                    "team_city": row.team_city,
                    "team_name": row.team_name,
                }
            )

    return json

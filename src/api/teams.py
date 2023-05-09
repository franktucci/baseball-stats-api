from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query
from sqlalchemy import create_engine
import os
import dotenv
import sqlalchemy
import dotenv

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
    created_by = "created_by"


# Add get parameters
@router.get("/teams/", tags=["teams"])
def list_teams(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: team_sort_options = team_sort_options.team_name,
):
    """
    This endpoint returns a list of teams in 2022. For each team it returns:

team_id: The internal id of the team. Can be used to query the /teams/{team_id} endpoint.
created_by: The user who created the team. Is null for real-life teams.
team_city: The city the team is located in. Can be null for fictional teams.
team_name: The name of the team.
You can filter for teams whose name contains a string by using the name or created by by using the created_by
query parameters, as well as real=True for only real-life teams.
    """

    if sort is team_sort_options.team_name:
        order_by = db.teams.c.team_name
    elif sort is team_sort_options.created_by:
        order_by = db.teams.c.created_by
    else:
        assert False

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

    # filter only if name parameter is passed
    if name != "":
        stmt = stmt.where(db.teams.c.team_name.ilike(f"%{name}%"))

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

@router.put("/teams/{team_id}", tags=["teams"])
def put_team(team_id: int):
    """
    This endpoint adds a team roster if the id does not exist, otherwise overwrites an existing team if the team_id is the same.
    This endpoint must take a non-null value for the created_by section as it cannot overwrite a real-life team. Accepts a team object:

team_id: The internal id of the team. Can be used to query the /teams/{team_id} endpoint.
created_by: The user who created the team. Is null for real-life teams.
team_city: The city the team is located in. Can be null for virtual teams.
team_name: The name of the team.
players: A list of the team's player_id's. Technically, a user-created team could have no players.
    """

    stmt = (
        sqlalchemy.select(
            db.movies.c.movie_id,
            db.movies.c.title,
            db.characters.c.name,
        )
        .select_from(db.movies)
        .join(db.characters)
        .join(db.lines)
        .where(db.movies.c.movie_id==team_id)
    )

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    # "movie_id": row.movie_id,
                    # "movie_title": row.title,
                    # "name": row.name,
                }
            )

    return json

@router.delete("/teams/{team_id}", tags=["teams"])
def delete_team(team_id: int):
    """
    This endpoint deletes the specified team by team_id. Will not delete a real-life team.
    """

    stmt = (
        sqlalchemy.select(
            db.movies.c.movie_id,
            db.movies.c.title,
            db.characters.c.name,
        )
        .select_from(db.movies)
        .join(db.characters)
        .join(db.lines)
        .where(db.movies.c.movie_id==team_id)
    )

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    # "movie_id": row.movie_id,
                    # "movie_title": row.title,
                    # "name": row.name,
                }
            )

    return json

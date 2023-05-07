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

@router.get("/events/{event_id}", tags=["events"])
def get_event(event_id: int):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
      are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.
    """

    stmt = (
        sqlalchemy.select(
            db.events.c.event_id,
            db.events.c.game_id,
            db.events.c.inning,
            db.T_B.c.T_B,
            db.events.c.player_id,
            db.events.c.performance_enum,
        )
        .select_from(db.events)
        .join(db.characters)
        .join(db.lines)
        .where(db.events.c.event_id==event_id)
    )

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "event_id": row.event_id,
                    "game_id": row.game_id,
                    "inning": row.inning,
                    "T_B": row.T_B,
                    "player_id": row.player_id,
                    "performance_enum": row.performance_enum
                }
            )

    return json


class event_sort_options(str, Enum):
    inning = "inning"
    T_B = "T_B"


# Add get parameters
@router.get("/events/", tags=["events"])
def list_movies(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: event_sort_options = event_sort_options.inning,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    if sort is event_sort_options.inning:
        order_by = db.events.c.inning
    elif sort is event_sort_options.T_B:
        order_by = db.events.c.T_B
    else:
        assert False

    stmt = (
        sqlalchemy.select(
            db.events.c.event_id,
            db.events.c.game_id,
            db.events.c.inning,
            db.events.c.T_B,
            db.events.c.player_id,
            db.events.c.performance_enum,
        )
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.events.c.event_id)
    )

    # filter only if name parameter is passed
    if name != "":
        stmt = stmt.where(db.events.c.inning.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "event_id": row.event_id,
                    "game_id": row.game_id,
                    "inning": row.inning,
                    "T_B": row.T_B,
                    "player_id": row.player_id,
                    "performance_enum": row.performance_enum
                }
            )

    return json
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

@router.get("/players/{player_id}", tags=["players"])
def get_player(player_id: int):
    """
    This endpoint returns a player's stats for 2022.

    * `player_id`: The internal id of the player. Can be used to query the
      `/view_player/{player_id}` endpoint.
    * `player_name`: The name of the player.
    * `created_by`: The user who created the team. Is null for real-life teams.
    * `positions`: A list of position_ids that the player is able to play.
    * `at_bat`: The number of times a player has been up to bat, total.
    * `runs`: The number of runs scored by the player.
    * `hits`: The number of times the ball is hit and the batter gets to at least first base.
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
            db.players.c.player_name,
        )
        .where(db.players.c.player_id == player_id)
    )
    with db.engine.connect() as conn:
        players_result = conn.execute(stmt)

    player = players_result.first()

    if player is None:
         raise HTTPException(status_code=404, detail="player not found.")

    return {
        'player_id': player_id,
        'player_name': player.player_name
    }


class players_sort_options(str, Enum):
    player_name = "player_name"
    # year = "year"
    # rating = "rating"


# Add get parameters
@router.get("/players/", tags=["movies"])
def list_players(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: players_sort_options = players_sort_options.player_name,
):
    """
    This endpoint returns a list of players in 2022. For each player it returns:

    * `player_id`: The internal id of the player. Can be used to query the
      `/players/{player_id}` endpoint.
    * `player_name`: The name of the player.
    * `created_by`: The user who created the team. Is null for real-life teams.
    * `positions`: A list of position_ids that the player is able to play.
    * `at_bat`: The number of times a player has been up to bat, total.
    * `runs`: The number of runs scored by the player.
    * `hits`: The number of times the ball is hit and the batter gets to at least first base.
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
    """

    # if sort is movie_sort_options.movie_title:
    #     order_by = db.movies.c.title
    # elif sort is movie_sort_options.year:
    #     order_by = db.movies.c.year
    # elif sort is movie_sort_options.rating:
    #     order_by = sqlalchemy.desc(db.movies.c.imdb_rating)
    # else:
    #     assert False
    #
    # stmt = (
    #     sqlalchemy.select(
    #         db.movies.c.movie_id,
    #         db.movies.c.title,
    #         db.movies.c.year,
    #         db.movies.c.imdb_rating,
    #         db.movies.c.imdb_votes,
    #     )
    #     .limit(limit)
    #     .offset(offset)
    #     .order_by(order_by, db.movies.c.movie_id)
    # )
    #
    # # filter only if name parameter is passed
    # if name != "":
    #     stmt = stmt.where(db.movies.c.title.ilike(f"%{name}%"))
    #
    # with db.engine.connect() as conn:
    #     result = conn.execute(stmt)
    #     json = []
    #     for row in result:
    #         json.append(
    #             {
    #                 "movie_id": row.movie_id,
    #                 "movie_title": row.title,
    #                 "year": row.year,
    #                 "imdb_rating": row.imdb_rating,
    #                 "imdb_votes": row.imdb_votes,
    #             }
    #         )

    json = {}
    return json
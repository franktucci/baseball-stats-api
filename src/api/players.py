from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query
import sqlalchemy
from pydantic import BaseModel
from Crypto.Hash import SHA256

router = APIRouter()

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

def calculate_hits(row):
    return row.single_count + row.double_count + row.triple_count + row.hr_count
def calculate_at_bats(row):
    return calculate_hits(row) + row.walk_count + row.strike_out_count + row.hit_by_pitch_count + row.sac_fly_count + row.other_out_count
def calculate_obp(row):
    numerator = calculate_hits(row) + row.walk_count + row.hit_by_pitch_count
    denominator = calculate_at_bats(row) + row.walk_count + row.hit_by_pitch_count + row.sac_fly_count
    return 0.0 if denominator == 0 else round(numerator / denominator, 3)
def calculate_avg(row):
    return 0.0 if calculate_at_bats(row) == 0 else round(calculate_hits(row) / calculate_at_bats(row), 3)

def filter_helper(e):
    return sqlalchemy.funcfilter(sqlalchemy.func.count(db.events.c.enum), sqlalchemy.and_((db.events.c.enum == e.value), sqlalchemy.or_(db.events.c.player_id > 1682, sqlalchemy.and_((db.events.c.player_id <= 1682), (db.events.c.game_id <= 2429))))).label(e.name.lower() + '_count')

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
    """

    stmt = (
        sqlalchemy.select(
            db.players.c.player_id,
            db.players.c.first_name,
            db.players.c.last_name,
            db.players.c.team_id,
            db.players.c.created_by,
            db.players.c.position,
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
        .group_by(db.players.c.player_id)
        .where(db.players.c.player_id == player_id)
    )
    with db.engine.connect() as conn:
        players_result = conn.execute(stmt)

    player = players_result.first()

    if player is None:
         raise HTTPException(status_code=404, detail="player not found.")

    return {
        'player_id': player_id,
        'player_name': player.first_name + " " + player.last_name,
        'created_by': player.created_by,
        'team_id': player.team_id,
        'positions': player.position,
        'at_bat': calculate_at_bats(player),
        'singles': player.single_count,
        'doubles': player.double_count,
        'triples': player.double_count,
        'home_runs': player.hr_count,
        'walks': player.walk_count,
        'strike_outs': player.strike_out_count,
        'hit_by_pitch': player.hit_by_pitch_count,
        'sacrifice_flies': player.sac_fly_count,
        'stolen_bases': player.stolen_count,
        'caught_stealing': player.caught_stealing_count,
        'on_base_percent': calculate_obp(player),
        'batting_average': calculate_avg(player)
    }

class PlayerJson(BaseModel):
    first_name: str
    last_name: str
    team_id: int
    created_by: str
    password: str
    position: str

@router.post("/players/", tags=["players"])
def add_player(player: PlayerJson):
    """
    This endpoint takes in a `first_name`, `last_name`, `team_id`, `created_by`,
    `password`, and `position`.

    `position` can be one of the following options: 1B, 2B, SS, 3B, IF, OF, P, C, DH

    The endpoint returns the id of the resulting player that was created.
    """

    if player.created_by is None:
        raise HTTPException(status_code=422, detail="must specify a username.")
    if player.position not in ['1B', '2B', 'SS', '3B', 'IF', 'OF', 'P', 'C', 'DH']:
        raise HTTPException(status_code=422, detail="incorrect position option.")

    stmt = (
        sqlalchemy.select(
            db.users.c.username,
            db.users.c.password_hash
        )
        .where(db.users.c.username == player.created_by)
    )

    with db.engine.connect() as conn:
        user_result = conn.execute(stmt)

    user = user_result.first()
    if user is None:
        raise HTTPException(status_code=422, detail="user is not registered. Register at /users/.")

    d = SHA256.new()
    d.update(bytes(player.password, 'utf8'))
    if d.hexdigest() != user.password_hash:
        raise HTTPException(status_code=422, detail="incorrect password.")

    stmt = (
        sqlalchemy.select(
            db.teams.c.team_id,
            db.teams.c.created_by
        )
        .where(db.teams.c.team_id == player.team_id)
    )
    with db.engine.connect() as conn:
        team_result = conn.execute(stmt)

    team = team_result.first()
    if team is None:
        raise HTTPException(status_code=422, detail="team must exist.")

    if not team.created_by or team.created_by != user.username:
        raise HTTPException(status_code=422, detail="can't add a player to a team that isn't yours!")

    with db.engine.begin() as conn:
        players_result = conn.execute(
            db.players.insert().values(
                created_by=player.created_by,
                team_id=player.team_id,
                first_name=player.first_name,
                last_name=player.last_name,
                position=player.position
            ).returning(db.players.c.player_id)
        )
    return {'player_id': players_result.first().player_id}
class players_sort_options(str, Enum):
    player_id = "id"
    player_name = "name"

class players_show_options(str, Enum):
    real = "real"
    fake = "fake"
    both = "both"

@router.get("/players/", tags=["players"])
def list_players(
    name: str = "",
    created: str = "",
    team: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: players_sort_options = players_sort_options.player_id,
    show: players_show_options = players_show_options.fake,
):
    """
    This endpoint returns a list of players in 2022. For each player it returns:

    * `player_id`: The internal id of the player. Can be used to query the
      `/players/{player_id}` endpoint.
    * `player_name`: The name of the player.
    * `team_name`: The team name of the player.
    * `created_by`: The user who created the team. Is null for real-life teams.
    * `positions`: A string representing the positions the player can play.
    * `at_bats`: The number of times a player has been up to bat.
    * `on_base_percent`: Calculated (Hit + Ball + HBP) / (At-Bat + Walk + HBP + Sacrifice-Fly)
    * `batting_average`: Calculated Hit / At-bat

    You can filter for players whose name contains a string by using the
    `name`, `team`, `created` query parameters.

    You can filter the results by using the `show` query parameter:
    * `real` - Real life players only.
    * `fake` - Fake players only.
    * `both` - Both real and fake players.

    You can sort the results by using the `sort` query parameter:
    * `id` - Sort by player_id.
    * `name` - Sort by first name alphabetically.
    """

    if sort is players_sort_options.player_name:
        order_by = db.players.c.first_name
    elif sort is players_sort_options.player_id:
        order_by = db.players.c.player_id
    else:
        raise HTTPException(status_code=422, detail="invalid sort query parameter.")

    if show is players_show_options.real:
        show_by = db.players.c.created_by == None
    elif show is players_show_options.fake:
        show_by = db.players.c.created_by != None
    elif show is players_show_options.both:
        show_by = True
    else:
        raise HTTPException(status_code=422, detail="incorrect show query parameter.")

    stmt = (
        sqlalchemy.select(
            db.players.c.player_id,
            db.players.c.first_name,
            db.players.c.last_name,
            db.teams.c.team_name,
            db.players.c.created_by,
            db.players.c.position,
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
        .select_from(db.players.join(db.events, db.events.c.player_id == db.players.c.player_id, isouter=True).join(db.teams, db.players.c.team_id == db.teams.c.team_id, isouter=True))
        .limit(limit)
        .offset(offset)
        .where(show_by)
        .group_by(db.players.c.player_id, db.teams.c.team_name)
        .order_by(order_by, db.players.c.player_id)
    )

    if name != "":
        stmt = stmt.where(db.players.c.first_name.ilike(f"{name}%"))
    if created != "":
        stmt = stmt.where(db.players.c.created_by.ilike(f"{created}%"))
    if team != "":
        stmt = stmt.where(db.teams.c.team_name.ilike(f"{team}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    'player_id': row.player_id,
                    'player_name': row.first_name + " " + row.last_name,
                    'team_name': row.team_name,
                    'created_by': row.created_by,
                    'positions': row.position,
                    'at_bats': calculate_at_bats(row),
                    'on_base_percent': calculate_obp(row),
                    'batting_average': calculate_avg(row)
                }
            )

    return json

class DeletePlayerJson(BaseModel):
    password: str
@router.delete("/players/{player_id}", tags=["players"])
def delete_player(player_id: int, password: DeletePlayerJson):
    """
    This endpoint deletes a player. It takes in a `password`.

    The endpoint returns the id of the resulting player that was deleted.
    """
    stmt = (
        sqlalchemy.select(
            db.players.c.password_hash)
        .where(db.players.c.player_id == player_id)
        .join(db.users, db.users.c.username == db.users.c.created_by)
    )
    with db.engine.begin() as conn:
        result = conn.execute(stmt)
        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Player not found.")
        delete_result = conn.execute(
            db.players.delete().where(db.players.c.player_id == player_id)
        )
    if delete_result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Player not found.")
    return {"message": "Player deleted successfully."}

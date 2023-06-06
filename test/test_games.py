from fastapi.testclient import TestClient
from src import database as db
from src import datatypes
import sqlalchemy
from src.api import games
from src.api.server import app
from test import baseball_factory as bf
from faker import Faker
from Crypto.Hash import SHA256

client = TestClient(app)

def test_get_game():
    password = Faker().word()
    d = SHA256.new()
    d.update(bytes(password, 'utf8'))

    user = bf.UserFactory(password_hash=d.hexdigest())
    team_1 = bf.TeamFactory(created_by=user.username)
    team_2 = bf.TeamFactory(created_by=user.username)

    with db.engine.connect() as conn:
        team_input = vars(team_1)
        del team_input['team_id']
        team_1_result = conn.execute(
            sqlalchemy.insert(db.teams).returning(db.teams.c.team_id), team_input
        )
        team_input = vars(team_2)
        del team_input['team_id']
        team_2_result = conn.execute(
            sqlalchemy.insert(db.teams).returning(db.teams.c.team_id), team_input
        )

    team_1_id = team_1_result.first().team_id
    team_2_id = team_2_result.first().team_id

    players = []

    for i in range(20):
        player = vars(bf.PlayerFactory(team_id=(team_1_id if i < 10 else team_2_id), created_by=user.username))
        del player['player_id']
        players.append(player)

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.insert(db.users), [vars(user)])
        players_result = conn.execute(db.players.insert().returning(db.players.c.player_id), players)

    player_id = players_result.first().player_id
    response = client.post('/games',
        json={
              "created_by": user.username,
              "password": password,
              "lineup1": {
                "team_id": team_1_id,
                "lineup": [i for i in range(player_id, player_id + 10)]
              },
              "lineup2": {
                "team_id": team_2_id,
                "lineup": [i for i in range(player_id + 10, player_id + 20)]
              }
            }
    )
    json = response.json()

    with db.engine.connect() as conn:
        games_result = conn.execute(sqlalchemy.select('*').where(db.games.c.game_id == json['game_id']))
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.users).where(db.users.c.username == user.username))
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.team_id == team_1_id))
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.team_id == team_2_id))
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team_1_id))
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team_2_id))
        conn.execute(sqlalchemy.delete(db.events).where(db.events.c.game_id == json['game_id']))
        conn.execute(sqlalchemy.delete(db.games).where(db.games.c.game_id == json['game_id']))

    assert response.status_code == 200
    assert json['events']
    assert len(json['events']) > 0
def test_event():
    player = bf.PlayerStatsFactory()
    bases = [False, False, False]
    event, outs, runs = games.simulate_event(1, 0, player, bases)

    assert event['player_id'] == player.player_id
    assert event['inning'] == 1
    assert event['B/T'] == 0
    assert 0 <= event['enum'] <= 10


def test_half():
    with db.engine.connect() as conn:
        players_result = conn.execute(sqlalchemy.select(db.players.c.player_id).order_by(sqlalchemy.desc('player_id')))

    player_id = players_result.first().player_id + 1

    lineup = []
    player_stats = {}

    for i in range(10):
        lineup.append(player_id)
        player_stats[player_id] = bf.PlayerStatsFactory()
        player_id += 1

    half_events, half_runs, order = games.simulate_half(1, 0, player_stats, lineup, 1)

    assert len(half_events) > 0
    assert 1 <= order <= 10

def test_inning():
    with db.engine.connect() as conn:
        players_result = conn.execute(sqlalchemy.select(db.players.c.player_id).order_by(sqlalchemy.desc('player_id')))

    player_id = players_result.first().player_id + 1

    player_stats = {}
    home_lineup = []

    for i in range(10):
        home_lineup.append(player_id)
        player_stats[player_id] = bf.PlayerStatsFactory()
        player_id += 1

    away_lineup = []

    for i in range(10):
        away_lineup.append(player_id)
        player_stats[player_id] = bf.PlayerStatsFactory()
        player_id += 1

    inn_events, inn_runs_home, inn_runs_away, inn_order_home, inn_order_away = games.simulate_inning(1, player_stats, [home_lineup, away_lineup], [1, 1])


    assert len(inn_events) > 0
    assert 1 <= inn_order_home <= 10
    assert 1 <= inn_order_away <= 10

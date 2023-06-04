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

def test_game():
    with db.engine.connect() as conn:
        players_result = conn.execute(sqlalchemy.select(db.players.c.player_id).order_by(sqlalchemy.desc('player_id')))
        teams_result = conn.execute(sqlalchemy.select(db.teams.c.team_id).order_by(sqlalchemy.desc('team_id')))
        games_result = conn.execute(sqlalchemy.select(db.games.c.game_id).order_by(sqlalchemy.desc('game_id')))
    player_id = players_result.first().player_id + 1
    team_id = teams_result.first().team_id + 1
    game_id = 1 if not games_result.first() else games_result.first().game_id + 1

    password = Faker().word()
    d = SHA256.new()
    d.update(bytes(password, 'utf8'))

    user = bf.UserFactory(password_hash=d.hexdigest())
    team_1 = bf.TeamFactory(team_id=team_id, created_by=user.username)
    team_2 = bf.TeamFactory(team_id=team_id + 1, created_by=user.username)

    players = []

    for i in range(20):
        player = bf.PlayerFactory(player_id=player_id, team_id=team_id + (i // 10), created_by=user.username)
        players.append(
            {
                "player_id": player.player_id,
                "created_by": player.created_by,
                "team_id": player.team_id,
                "first_name": player.first_name,
                "last_name": player.last_name,
                "position": player.position
            }
        )
        player_id += 1

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.insert(db.users), [vars(user)])
        conn.execute(sqlalchemy.insert(db.teams), [vars(team_1)])
        conn.execute(sqlalchemy.insert(db.teams), [vars(team_2)])
        conn.execute(db.players.insert(), players)

    response = client.post('/games',
        json={
              "created_by": user.username,
              "password": password,
              "lineup1": {
                "team_id": team_1.team_id,
                "lineup": [
                  i['player_id'] for i in players[:10]
                ]
              },
              "lineup2": {
                "team_id": team_2.team_id,
                "lineup": [
                  i['player_id'] for i in players[10:]
                ]
              }
            }
    )
    json = response.json()

    with db.engine.connect() as conn:
        games_result = conn.execute(sqlalchemy.select('*').where(db.games.c.game_id == game_id))
    game = games_result.first()
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.users).where(db.users.c.username == user.username))
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.team_id == team_1.team_id))
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.team_id == team_2.team_id))
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team_1.team_id))
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team_2.team_id))
        conn.execute(sqlalchemy.delete(db.events).where(db.events.c.game_id == game_id))
        conn.execute(sqlalchemy.delete(db.games).where(db.games.c.game_id == game_id))

    assert response.status_code == 200
    assert json['game_id'] == game_id
    assert game.game_id == game_id
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

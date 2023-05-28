from fastapi.testclient import TestClient
from src import database as db
from src import datatypes
import sqlalchemy
from src.api import games
from src.api.server import app
from test import baseball_factory as bf

client = TestClient(app)

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

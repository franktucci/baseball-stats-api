from fastapi.testclient import TestClient

from src import datatypes
from src.api import games
from src.api.server import app

import json
import factory
import random

client = TestClient(app)

class PlayerStats:
    player_id: int
    single_count: int
    double_count: int
    triple_count: int
    hr_count: int
    walk_count: int
    strike_out_count: int
    hit_by_pitch_count: int
    sac_fly_count: int
    other_prp: int

class PlayerStatsFactory:
    player_id = 0
    single_count = random.randrange(0, 10)
    double_count = random.randrange(0, 10)
    triple_count = random.randrange(0, 10)
    hr_count = random.randrange(0, 10)
    walk_count = random.randrange(0, 10)
    strike_out_count = random.randrange(0, 10)
    hit_by_pitch_count = random.randrange(0, 10)
    sac_fly_count = random.randrange(0, 10)
    other_out_count = random.randrange(0, 10)
    class Meta:
        model = PlayerStats

class PlayerFactory(factory.Factory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    position = factory.Faker('text')
    created_by = 'castindico'
    player_id = 0
    team_id = 0
    class Meta:
        model = datatypes.Player

# def test_get_game_by_id():
#     response = client.get("/games/133")
#     assert response.status_code == 200
#
#     with open("test/games/133.json", encoding="utf-8") as f:
#         assert response.json() == json.load(f)
#
# def test_get_game_by_id_2():
#     response = client.get("/games/19757")
#     assert response.status_code == 200
#
#     with open("test/games/19757.json", encoding="utf-8") as f:
#         assert response.json() == json.load(f)
#
# def test_get_games():
#     response = client.get("/games/")
#     assert response.status_code == 200
#
#     with open("test/games/root.json", encoding="utf-8") as f:
#         assert response.json() == json.load(f)
#
# def test_sort_filter():
#     response = client.get("/games/?name=amy&limit=10")
#     assert response.status_code == 200
#
#     with open(
#         "test/games/lines-name=amy&limit=10.json",
#         encoding="utf-8",
#     ) as f:
#         assert response.json() == json.load(f)
#
# def test_sort_filter_2():
#     response = client.get("/games/?text=said&offset=30&limit=10&sort=conversation")
#     assert response.status_code == 200
#
#     with open(
#         "test/games/lines-text=said&offset=30&limit=10&sort=conversation.json",
#         encoding="utf-8",
#     ) as f:
#         assert response.json() == json.load(f)

# def test_404():
#     response = client.get("/games/-1")
#     assert response.status_code == 404

def test_event():
    player = PlayerStatsFactory()
    bases = [False, False, False]
    event, outs, runs = games.simulate_event(1, 0, player, bases)
    assert event is not None
    assert event['player_id'] == player.player_id
    assert event['inning'] == 1
    assert event['B/T'] == 0
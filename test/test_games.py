from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_game_by_id():
    response = client.get("/games/133")
    assert response.status_code == 200

    with open("test/games/133.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_game_by_id_2():
    response = client.get("/games/19757")
    assert response.status_code == 200

    with open("test/games/19757.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_games():
    response = client.get("/games/")
    assert response.status_code == 200

    with open("test/games/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_sort_filter():
    response = client.get("/games/?name=amy&limit=10")
    assert response.status_code == 200

    with open(
        "test/games/lines-name=amy&limit=10.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_2():
    response = client.get("/games/?text=said&offset=30&limit=10&sort=conversation")
    assert response.status_code == 200

    with open(
        "test/games/lines-text=said&offset=30&limit=10&sort=conversation.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_404():
    response = client.get("/games/1")
    assert response.status_code == 404

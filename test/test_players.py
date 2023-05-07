from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_player_by_id():
    response = client.get("/players/7421")
    assert response.status_code == 200

    with open("test/players/7421.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_player_by_id_2():
    response = client.get("/players/4")
    assert response.status_code == 200

    with open("test/players/4.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_players():
    response = client.get("/players/")
    assert response.status_code == 200

    with open("test/players/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter():
    response = client.get(
        "/players/?name=amy&limit=50&offset=0&sort=number_of_lines"
    )
    assert response.status_code == 200

    with open(
        "test/players/characters-name=amy&limit=50&offset=0&sort=number_of_lines.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_2():
    response = client.get(
        "/players/?offset=30&limit=10&sort=movie"
    )
    assert response.status_code == 200

    with open(
        "test/players/characters-offset=30&limit=10&sort=movie.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_404():
    response = client.get("/players/400")
    assert response.status_code == 404

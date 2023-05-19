from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_player_by_id():
    response = client.get("/players/29")
    assert response.status_code == 200

    with open("test/players/29.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_player_by_id_2():
    response = client.get("/players/52")
    assert response.status_code == 200

    with open("test/players/52.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_players():
    response = client.get("/players/")
    assert response.status_code == 200

    with open("test/players/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_players_2():
    response = client.get("/players/")
    assert response.status_code == 200

    with open("test/players/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_put_player():
    response = client.get("/players/(id)")
    assert response.status_code == 200

    with open("test/players/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_put_player_2():
    response = client.get("/players/(id)")
    assert response.status_code == 200

    with open("test/players/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_delete_player():
    response = client.get("/players/(id)")
    assert response.status_code == 200

    with open("test/players/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_delete_player_2():
    response = client.get("/players/(id)")
    assert response.status_code == 200

    with open("test/players/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter():
    response = client.get(
        "/players/?name=mike&limit=50&offset=0&sort=name"
    )
    assert response.status_code == 200

    with open(
        "test/players/players-name=mike&limit=50&offset=0&sort=name.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_2():
    response = client.get(
        "/players/?offset=30&limit=10&sort=name"
    )
    assert response.status_code == 200

    with open(
        "test/players/characters-offset=30&limit=10&sort=name.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_404():
    response = client.get("/players/400")
    assert response.status_code == 404

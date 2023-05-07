from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_team_by_id():
    response = client.get("/teams/44")
    assert response.status_code == 200

    with open("test/teams/44.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_team_by_id_2():
    response = client.get("/teams/0")
    assert response.status_code == 200

    with open("test/teams/0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_teams():
    response = client.get("/teams/")
    assert response.status_code == 200

    with open("test/teams/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_put_teams():
    response = client.get("/teams/(id)")
    assert response.status_code == 200

    with open("test/teams/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_put_team_2():
    response = client.get("/teams/(id)")
    assert response.status_code == 200

    with open("test/teams/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_delete_team():
    response = client.get("/teams/(id)")
    assert response.status_code == 200

    with open("test/players/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_delete_team_2():
    response = client.get("/teams/(id)")
    assert response.status_code == 200

    with open("test/players/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter():
    response = client.get("/teams/?name=big&limit=50&offset=0&sort=rating")
    assert response.status_code == 200

    with open(
        "test/teams/movies-name=big&limit=50&offset=0&sort=rating.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_2():
    response = client.get("/teams/?offset=30&limit=10&sort=rating")
    assert response.status_code == 200

    with open(
        "test/teams/movies-offset=30&limit=10&sort=rating.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_404():
    response = client.get("/teams/1")
    assert response.status_code == 404

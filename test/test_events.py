from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_event_by_id():
    response = client.get("/events/133")
    assert response.status_code == 200

    with open("test/events/133.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_event_by_id_2():
    response = client.get("/events/19757")
    assert response.status_code == 200

    with open("test/events/19757.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_events():
    response = client.get("/events/")
    assert response.status_code == 200

    with open("test/events/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter():
    response = client.get("/events/?name=amy&limit=10")
    assert response.status_code == 200

    with open(
        "test/events/lines-name=amy&limit=10.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_2():
    response = client.get("/events/?text=said&offset=30&limit=10&sort=conversation")
    assert response.status_code == 200

    with open(
        "test/events/lines-text=said&offset=30&limit=10&sort=conversation.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_404():
    response = client.get("/events/1")
    assert response.status_code == 404

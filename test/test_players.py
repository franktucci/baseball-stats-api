from fastapi.testclient import TestClient
from src.api.server import app
from src import database as db
from test import baseball_factory
import sqlalchemy
from test import baseball_factory as bf
import json
from faker import Faker
from Crypto.Hash import SHA256

client = TestClient(app)


def test_get_player():
    with db.engine.connect() as conn:
        players_result = conn.execute(sqlalchemy.select(db.players.c.player_id).order_by(sqlalchemy.desc('player_id')))
    player_id = players_result.first().player_id + 1
    player = bf.PlayerFactory(player_id=player_id)
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.insert(db.players), [vars(player)])

    response = client.get("/players/" + str(player.player_id))
    json = response.json()

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.player_id == player_id))

    assert response.status_code == 200
    assert json['player_id'] == player.player_id
    assert json['player_name'] == player.first_name + ' ' + player.last_name
    assert json['created_by'] == player.created_by
    assert json['team_id'] == player.team_id
    assert json['positions'] == player.position

def test_add_player():
    with db.engine.connect() as conn:
        players_result = conn.execute(sqlalchemy.select(db.players.c.player_id).order_by(sqlalchemy.desc('player_id')))
        teams_result = conn.execute(sqlalchemy.select(db.teams.c.team_id).order_by(sqlalchemy.desc('team_id')))
    player_id = players_result.first().player_id + 1
    team_id = teams_result.first().team_id + 1

    password = Faker().word()
    d = SHA256.new()
    d.update(bytes(password, 'utf8'))

    user = bf.UserFactory(password_hash=d.hexdigest())
    team = bf.TeamFactory(team_id=team_id, created_by=user.username)
    player = bf.PlayerFactory(player_id=player_id, created_by=user.username, team_id=team.team_id)

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.insert(db.users), [vars(user)])
        conn.execute(sqlalchemy.insert(db.teams), [vars(team)])

    response = client.post('/players/',
        json={
            "first_name": player.first_name,
            "last_name": player.last_name,
            "team_id": team.team_id,
            "created_by": user.username,
            "password": password,
            "position": player.position
        }
    )
    json = response.json()

    with db.engine.connect() as conn:
        players_result = conn.execute(sqlalchemy.select('*').where(db.players.c.player_id == player.player_id))
        events_result = conn.execute(sqlalchemy.select('*').where(db.events.c.player_id == player.player_id))
    player2 = players_result.first()
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.player_id == player.player_id))
        conn.execute(sqlalchemy.delete(db.users).where(db.users.c.username == user.username))
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team.team_id))

    assert response.status_code == 200
    assert json['player_id'] == player.player_id
    assert player.player_id == player2.player_id
    assert player.created_by == player2.created_by
    assert player.team_id == player2.team_id
    assert player.first_name == player2.first_name
    assert player.last_name == player2.last_name
    assert player.position == player2.position
    assert events_result.first() is None

def test_list_players():
    with db.engine.connect() as conn:
        players_result = conn.execute(sqlalchemy.select(db.players.c.player_id).order_by(sqlalchemy.desc('player_id')))
        teams_result = conn.execute(sqlalchemy.select(db.teams.c.team_id).order_by(sqlalchemy.desc('team_id')))
    player_id = players_result.first().player_id + 1
    team_id = teams_result.first().team_id + 1

    user = bf.UserFactory()
    team = bf.TeamFactory(team_id=team_id, created_by=user.username)

    players = []

    for i in range(10):
        players.append(bf.PlayerFactory(player_id=player_id, created_by=user.username, team_id=team.team_id))
        player_id += 1

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.insert(db.teams), [vars(team)])
        for player in players:
            conn.execute(sqlalchemy.insert(db.players), [vars(player)])

    response = client.get("/players/?team=" + str(team.team_name))
    json = response.json()

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.player_id.in_(range(player_id - 10, player_id))))
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team.team_id))

    assert response.status_code == 200
    for i in range(10):
        assert response.status_code == 200
        assert json[i]['player_id'] == players[i].player_id
        assert json[i]['player_name'] == players[i].first_name + ' ' + players[i].last_name
        assert json[i]['created_by'] == players[i].created_by
        assert json[i]['team_name'] == team.team_name
        assert json[i]['positions'] == players[i].position


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
    player = bf.PlayerFactory()

    with db.engine.begin() as conn:
        player_input = vars(player)
        del player_input['player_id']
        players_result = conn.execute(sqlalchemy.insert(db.players).returning(db.players.c.player_id), player_input)

    player_id = players_result.first().player_id
    response = client.get("/players/" + str(player_id))
    json = response.json()

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.player_id == player_id))

    assert response.status_code == 200
    assert json['player_id'] == player_id
    assert json['player_name'] == player.first_name + ' ' + player.last_name
    assert json['created_by'] == player.created_by
    assert json['team_id'] == player.team_id
    assert json['positions'] == player.position

def test_add_player():
    password = Faker().word()
    d = SHA256.new()
    d.update(bytes(password, 'utf8'))

    user = bf.UserFactory(password_hash=d.hexdigest())
    team = bf.TeamFactory(created_by=user.username)

    with db.engine.begin() as conn:
        team_input = vars(team)
        del team_input['team_id']
        teams_result = conn.execute(sqlalchemy.insert(db.teams).returning(db.teams.c.team_id), team_input)
        conn.execute(sqlalchemy.insert(db.users), vars(user))
    team_id = teams_result.first().team_id

    player = bf.PlayerFactory(created_by=user.username, team_id=team_id)

    response = client.post('/players/',
        json={
            "first_name": player.first_name,
            "last_name": player.last_name,
            "team_id": team_id,
            "created_by": user.username,
            "password": password,
            "position": player.position
        }
    )
    json = response.json()
    print(json)
    player_id = json['player_id']
    with db.engine.connect() as conn:
        players_result = conn.execute(sqlalchemy.select('*').where(db.players.c.player_id == player_id))
        events_result = conn.execute(sqlalchemy.select('*').where(db.events.c.player_id == player_id))

    player2 = players_result.first()
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.player_id == player_id))
        conn.execute(sqlalchemy.delete(db.users).where(db.users.c.username == user.username))
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team_id))

    assert response.status_code == 200
    assert json['player_id'] == player_id
    assert player_id == player2.player_id
    assert player.created_by == player2.created_by
    assert player.team_id == player2.team_id
    assert player.first_name == player2.first_name
    assert player.last_name == player2.last_name
    assert player.position == player2.position
    assert events_result.first() is None

def test_list_players():
    user = bf.UserFactory()
    team = bf.TeamFactory(created_by=user.username)

    with db.engine.begin() as conn:
        team_input = vars(team)
        del team_input['team_id']
        teams_result = conn.execute(sqlalchemy.insert(db.teams).returning(db.teams.c.team_id), team_input)
    team_id = teams_result.first().team_id

    players = []

    for i in range(10):
        player = vars(bf.PlayerFactory(created_by=user.username, team_id=team_id))
        del player['player_id']
        players.append(player)

    with db.engine.begin() as conn:
        players_result = conn.execute(sqlalchemy.insert(db.players).returning(db.players.c.player_id), players)

    player_id = players_result.first().player_id
    response = client.get("/players/?team=" + str(team.team_name))
    json = response.json()

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.players).where(db.players.c.player_id.in_(range(player_id, player_id + 10))))
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team_id))

    assert response.status_code == 200
    for i in range(10):
        assert response.status_code == 200
        assert json[i]['player_name'] == players[i]['first_name'] + ' ' + players[i]['last_name']
        assert json[i]['created_by'] == players[i]['created_by']
        assert json[i]['team_name'] == team.team_name
        assert json[i]['positions'] == players[i]['position']


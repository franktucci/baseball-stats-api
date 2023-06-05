from fastapi.testclient import TestClient
from src.api.server import app
from src import database as db
import sqlalchemy
from test import baseball_factory as bf
from faker import Faker
from Crypto.Hash import SHA256

client = TestClient(app)

def test_get_team():
    team = bf.TeamFactory()

    with db.engine.begin() as conn:
        team_input = vars(team)
        del team_input['team_id']
        teams_result = conn.execute(sqlalchemy.insert(db.teams).returning(db.teams.c.team_id), team_input)

    team_id = teams_result.first().team_id
    response = client.get("/teams/" + str(team_id))
    json = response.json()

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team_id))

    assert response.status_code == 200
    assert json['team_id'] == team_id
    assert json['created_by'] == team.created_by
    assert json['team_city'] == team.team_city
    assert json['team_name'] == team.team_name

def test_add_team():
    password = Faker().word()
    d = SHA256.new()
    d.update(bytes(password, 'utf8'))

    user = bf.UserFactory(password_hash=d.hexdigest())
    team = bf.TeamFactory(created_by=user.username)

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.insert(db.users), [vars(user)])

    response = client.post('/teams/',
        json={
                "team_city": team.team_city,
                "team_name": team.team_name,
                "created_by": team.created_by,
                "password": password
        }
    )
    json = response.json()

    with db.engine.connect() as conn:
        teams_result = conn.execute(sqlalchemy.select('*').where(db.teams.c.team_id == json['team_id']))
    team2 = teams_result.first()
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.users).where(db.users.c.username == user.username))
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id == team2.team_id))

    assert response.status_code == 200
    assert json['team_id'] == team2.team_id
    assert team.created_by == team2.created_by
    assert team.team_city == team2.team_city
    assert team.team_name == team2.team_name

def test_list_teams():
    user = bf.UserFactory()

    teams = []

    for i in range(10):
        team = vars(bf.TeamFactory(created_by=user.username))
        del team['team_id']
        teams.append(team)

    with db.engine.begin() as conn:
        teams_result = conn.execute(sqlalchemy.insert(db.teams).returning(db.teams.c.team_id), teams)

    team_id = teams_result.first().team_id
    response = client.get("/teams/?created=" + user.username)
    json = response.json()

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.teams).where(db.teams.c.team_id.in_(range(team_id, team_id + 10))))

    assert response.status_code == 200
    for i in range(10):
        assert json[i]['created_by'] == teams[i]['created_by']
        assert json[i]['team_city'] == teams[i]['team_city']
        assert json[i]['team_name'] == teams[i]['team_name']

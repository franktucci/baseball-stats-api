from fastapi.testclient import TestClient
from src.api.server import app
from src import database as db
from test import baseball_factory
import sqlalchemy
from test import baseball_factory as bf
import json
from Crypto.Hash import SHA256
import factory
from faker import Faker

client = TestClient(app)

def test_add_user():
    password = Faker().word()
    d = SHA256.new()
    d.update(bytes(password, 'utf8'))
    user = bf.UserFactory(password_hash=d.hexdigest())

    response = client.post('/users/',
        json={
           'username': user.username,
           'password': password
        }
    )
    json = response.json()

    with db.engine.connect() as conn:
        users_result = conn.execute(sqlalchemy.select(db.users.c.username, db.users.c.password_hash).where(db.users.c.username == user.username))
    user2 = users_result.first()
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.users).where(db.users.c.username == user.username))
    assert response.status_code == 200
    assert json['username'] == user.username
    assert user.username == user2.username
    assert user.password_hash == user2.password_hash


def test_422_existing_user():
    password = Faker().word()
    user = bf.UserFactory()
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.insert(db.users), [vars(user)])
    response = client.post('/users/',
        json={
           'username': user.username,
           'password': password
        }
    )

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.users).where(db.users.c.username == user.username))

    assert response.status_code == 422

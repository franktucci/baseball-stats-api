from fastapi.testclient import TestClient
from src import database as db
from src import datatypes
import sqlalchemy
from src.api import games
from src.api.server import app
from test import baseball_factory as bf
from faker import Faker

"""
**ONLY RUN THIS FILE WHEN CONNECTED TO LOCALHOST**
"""

def stress_test(num_entities):
    users = []
    players = []
    teams = []
    games = []
    events = []

    for i in range(num_entities):
        user = vars(bf.UserFactory())
        user['username'] = user['username'] + str(i)
        users.append(user)

        player = vars(bf.PlayerFactory())
        del player['player_id']
        players.append(player)

        team = vars(bf.TeamFactory())
        del team['team_id']
        teams.append(team)

        game = vars(bf.GameFactory())
        del game['game_id']
        games.append(game)

        event = vars(bf.EventFactory())
        del event['event_id']
        events.append(event)

    with db.engine.begin() as conn:
        conn.execute(db.users.insert(), users)
        conn.execute(db.players.insert(), players)
        conn.execute(db.teams.insert(), teams)
        conn.execute(db.games.insert(), games)
        conn.execute(db.events.insert(), events)

if __name__ == '__main__':
    stress_test(1000000)
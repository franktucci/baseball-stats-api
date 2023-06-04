"""create tables

Revision ID: 4042b94eb7d8
Revises: 
Create Date: 2023-05-22 14:11:28.236536

"""
from alembic import op
import sqlalchemy as sa
import csv


# revision identifiers, used by Alembic.
revision = '4042b94eb7d8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    event_enums = op.create_table(
        'event_enums',
        sa.Column('enum', sa.Integer, primary_key=True),
        sa.Column('string', sa.Text, nullable=False),
    )

    file_name = './data/event_enums_rows.csv'
    lines = list(csv.reader(open(file_name, 'r')))
    headers = lines.pop(0)
    data = [dict(zip(headers, line)) for line in lines]
    op.bulk_insert(event_enums, data)

    events = op.create_table(
        'events',
        sa.Column('event_id', sa.Integer, primary_key=True),
        sa.Column('inning', sa.Integer, nullable=False),
        sa.Column('BT', sa.Integer, nullable=False),
        sa.Column('game_id', sa.Integer, nullable=False),
        sa.Column('enum', sa.Integer, nullable=False),
        sa.Column('player_id', sa.Integer, nullable=False),
    )

    file_name = './data/events_rows.csv'
    lines = list(csv.reader(open(file_name, 'r')))
    headers = lines.pop(0)
    data = [dict(zip(headers, line)) for line in lines]
    op.bulk_insert(events, data)

    games = op.create_table(
        'games',
        sa.Column('game_id', sa.Integer, primary_key=True),
        sa.Column('created_by', sa.Text, nullable=True),
        sa.Column('home_team_id', sa.Integer, nullable=False),
        sa.Column('away_team_id', sa.Integer, nullable=False),
        sa.Column('home_score', sa.Integer, nullable=False),
        sa.Column('away_score', sa.Integer, nullable=False),
    )

    file_name = './data/games_rows.csv'
    lines = list(csv.reader(open(file_name, 'r')))
    headers = lines.pop(0)
    data = [dict(zip(headers, line)) for line in lines]
    for d in data:
        d['created_by'] = None
    op.bulk_insert(games, data)

    players = op.create_table(
        'players',
        sa.Column('player_id', sa.Integer, primary_key=True),
        sa.Column('created_by', sa.Text, nullable=True),
        sa.Column('team_id', sa.Integer, nullable=False),
        sa.Column('first_name', sa.Text, nullable=False),
        sa.Column('last_name', sa.Text, nullable=False),
        sa.Column('position', sa.Text, nullable=False),
    )

    file_name = './data/players_rows.csv'
    lines = list(csv.reader(open(file_name, 'r')))
    headers = lines.pop(0)
    data = [dict(zip(headers, line)) for line in lines]
    for d in data:
        d['created_by'] = None
    op.bulk_insert(players, data)

    teams = op.create_table(
        'teams',
        sa.Column('team_id', sa.Integer, primary_key=True),
        sa.Column('created_by', sa.Text, nullable=True),
        sa.Column('team_city', sa.Text, nullable=True),
        sa.Column('team_name', sa.Text, nullable=False),
    )

    file_name = './data/teams_rows.csv'
    lines = list(csv.reader(open(file_name, 'r')))
    headers = lines.pop(0)
    data = [dict(zip(headers, line)) for line in lines]
    for d in data:
        d['created_by'] = None
    op.bulk_insert(teams, data)

    op.create_table(
        'users',
        sa.Column('username', sa.Text, primary_key=True),
        sa.Column('password_hash', sa.Text, nullable=False)
    )

def downgrade() -> None:
    op.drop_table('event_enums')
    op.drop_table('events')
    op.drop_table('games')
    op.drop_table('players')
    op.drop_table('teams')
    op.drop_table('users')

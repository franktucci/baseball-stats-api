"""create tables

Revision ID: 4042b94eb7d8
Revises: 
Create Date: 2023-05-22 14:11:28.236536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4042b94eb7d8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'event_enums',
        sa.Column('enum', sa.Integer, primary_key=True),
        sa.Column('string', sa.text, nullable=False),
    )
    op.create_table(
        'events',
        sa.Column('event_id', sa.Integer, primary_key=True),
        sa.Column('inning', sa.Integer, nullable=False),
        sa.Column('BT', sa.Integer, nullable=False),
        sa.Column('game_id', sa.Integer, nullable=False),
        sa.Column('enum', sa.Integer, nullable=False),
        sa.Column('player_id', sa.Integer, nullable=False),
    )
    op.create_table(
        'games',
        sa.Column('game_id', sa.Integer, primary_key=True),
        sa.Column('created_by', sa.text, nullable=True),
        sa.Column('home_team_id', sa.Integer, nullable=False),
        sa.Column('away_team_id', sa.Integer, nullable=False),
        sa.Column('home_score', sa.Integer, nullable=False),
        sa.Column('away_score', sa.Integer, nullable=False),
    )
    op.create_table(
        'players',
        sa.Column('player_id', sa.Integer, primary_key=True),
        sa.Column('created_by', sa.text, nullable=True),
        sa.Column('team_id', sa.Integer, nullable=False),
        sa.Column('first_name', sa.text, nullable=False),
        sa.Column('last_name', sa.text, nullable=False),
        sa.Column('position', sa.text, nullable=False),
    )
    op.create_table(
        'event_enums',
        sa.Column('team_id', sa.Integer, primary_key=True),
        sa.Column('created_by', sa.text, nullable=True),
        sa.Column('team_city', sa.text, nullable=True),
        sa.Column('team_name', sa.text, nullable=False),
    )
    op.create_table(
        'event_enums',
        sa.Column('username', sa.text, primary_key=True),
        sa.Column('password_hash', sa.text, nullable=False)
    )

def downgrade() -> None:
    op.drop_table('event_enums')
    op.drop_table('events')
    op.drop_table('games')
    op.drop_table('players')
    op.drop_table('teams')
    op.drop_table('users')

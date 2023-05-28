import factory
from src import datatypes
import random

class PlayerFactory(factory.Factory):
    class Meta:
        model = datatypes.Player
    player_id = 0
    created_by = factory.Faker('user_name')
    team_id = 0
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    position = factory.Faker('random_element', elements=['1B', '2B', 'SS', '3B', 'IF', 'OF', 'P', 'C', 'DH'])


class GameFactory(factory.Factory):
    class Meta:
        model = datatypes.Game
    game_id = 0
    created_by = factory.Faker('user_name')
    home_score = factory.Faker('pyint', min_value=0, max_value=10)
    away_score = factory.Faker('pyint', min_value=0, max_value=10)
    home_team_id = 0
    away_team_id = 0


class EventFactory(factory.Factory):
    class Meta:
        model = datatypes.Event
    event_id = 0
    inning = factory.Faker('pyint', min_value=1, max_value=9)
    game_id = 0
    enum = factory.Faker('pyint', min_value=0, max_value=10)
    player_id = 0
    BT = factory.Faker('pyint', min_value=0, max_value=1)


class TeamFactory(factory.Factory):
    class Meta:
        model = datatypes.Team
    team_id = 0
    created_by = factory.Faker('user_name')
    team_city = factory.Faker('city')
    team_name = factory.Faker('word')


class UserFactory(factory.Factory):
    class Meta:
        model = datatypes.User
    username = factory.Faker('user_name')
    password_hash = format(random.getrandbits(256), 'x')


class PlayerStatsFactory(factory.Factory):
    class Meta:
        model = datatypes.PlayerStats
    player_id = 0
    single_count = factory.Faker('pyint', min_value=0, max_value=10)
    double_count = factory.Faker('pyint', min_value=0, max_value=10)
    triple_count = factory.Faker('pyint', min_value=0, max_value=10)
    hr_count = factory.Faker('pyint', min_value=0, max_value=10)
    walk_count = factory.Faker('pyint', min_value=0, max_value=10)
    strike_out_count = factory.Faker('pyint', min_value=0, max_value=10)
    hit_by_pitch_count = factory.Faker('pyint', min_value=0, max_value=10)
    sac_fly_count = factory.Faker('pyint', min_value=0, max_value=10)
    other_out_count = factory.Faker('pyint', min_value=0, max_value=10)

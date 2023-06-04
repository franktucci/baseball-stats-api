# baseball-stats-api

* Frank Tucci - ftucci@calpoly.edu
* Randall Caler - rcaler@calpoly.edu
* Sean Tomer - stomerho@calpoly.edu

### User flow:

As a baseball fan, I want a way to keep up with up-to-date statistics and follow up on how the season is going for each team and who the best players are. 

As a casual Seattle Mariners fan, I want to see how my team and its players are performing and how they stack up to other teams in an accessible, easy manner. 

As an enthusiastic sports better, I want to see who’s statistically on top and see who their best players are to most accurately predict who will win. 

As an avid baseball player, I want an outlet to make a team and play other teams in a simulated game based on real statistics in the current season of the MLB. 

---
### Intro:

Our API serves a twofold purpose. First, storing basic baseball statistics for every player, and keeping a team roster. We’re going to limit our initial version to only stats from the 2022 season, though we would be open to expanding our database to other seasons in the future. 

Secondly, we want to allow users to create their own fictional players and fictional reams with real or fictional players, and leverage those player stats to participate in simulated, randomized games. For example, if a player has a .250 batting average for the 2022 season, they would hit a .250 in the simulated game as well, etc, something not incredibly serious.

The API backend will service a website where it will be accessible to a user with or without an account. Should a user choose not to make an account, they will be able to check on player and team statistics for the 2022 season. The application will be easily accessible and have an intuitive interface that guides users to find both team statistics as well as individual player statistics. Should a user make an account, they will be able to save and recall their custom team and players to the database. Real-life teams are only viewable and are not editable. Users who wish to make small alterations to real-life teams will have the website create a clone of that player or team with the `created_by` data replaced with their username. We can easily imagine using an API key scheme attached to a user to prevent others from tampering/deleting your own teams, but this is something we need to research more into before committing to anything for the initial version.

---
### Endpoints:

GET /players/{player_id}

This endpoint returns a player's stats for 2022.
* `player_id`: The internal id of the player. Can be used to query the
  `/players/{player_id}` endpoint.
* `player_name`: The name of the player.
* `created_by`: The user who created the team. Is null for real-life teams.
* `team_id`: The internal id of the team the player plays on. Can be used to query the
  `/teams/{team_id}` endpoint.
* `positions`: A string representation of the positions a character can play.
* `at_bat`: The number of times a player has been up to bat, total.
* `singles`: The number of times the ball is hit and the batter gets to first base.
* `doubles`: The number of times the ball is hit and grants the batter 2 bases.
* `triples`: The number of times the ball is hit and grants the batter 3 bases.
* `home_runs`: The number of times the batter hits a home run.
* `walks`: The number of times the batter walks. This grants the batter one base.
* `strike_outs`: The number of times the batter strikes out.
* `hit_by_pitch`: The number of times the batter is hit by the pitch. This grants the batter one base.
* `sacrifice_flies`: The number of times the batter hits a fly ball that is caught out with less than two outs and, in the process, assists in a run.
* `stolen_bases`: The number of times a runner successfully has stolen a base.
* `caught_stealing`: The number of times a runner gets out in the process of stealing a base.
* `on_base_percent`: Calculated (Hit + Ball + HBP) / (At-Bat + Walk + HBP + Sacrifice-Fly)
* `batting_average`: Calculated Hit / At-bat

POST /players/

This endpoint takes in a `first_name`, `last_name`, `team_id`, `created_by`,
`password`, and `position`.

The endpoint returns the id of the resulting player that was created.

GET /players/

This endpoint returns a list of players in 2022. For each player it returns:
* `player_id`: The internal id of the player. Can be used to query the
  `/players/{player_id}` endpoint.
* `player_name`: The name of the player.
* `team_name`: The team name of the player.
* `created_by`: The user who created the team. Is null for real-life teams.
* `positions`: A string representing the positions the player can play.
* `at_bats`: The number of times a player has been up to bat.
* `on_base_percent`: Calculated (Hit + Ball + HBP) / (At-Bat + Walk + HBP + Sacrifice-Fly)
* `batting_average`: Calculated Hit / At-bat

You can filter for players whose name contains a string by using the
`name`, `team`, and/or `created` query parameters.

You can sort the results by using the `sort` query parameter:
* `id` - Sort by player_id.
* `name` - Sort by first name alphabetically.

GET /teams/{team_id}

This endpoint returns a team's information in 2022. It returns:
* `team_id`: The internal id of the team. Can be used to query the
  `/teams/{team_id}` endpoint.
* `created_by`: The user who created the team. Is null for real-life teams.
* `team_city`: The city the team is located in. Can be null for virtual teams.
* `team_name`: The name of the team.
* `players`: A list of the team's player_id's. Can be used to query the
  `/players/{player_id}` endpoint.

POST /teams/

This endpoint takes in a `team_name`, `team_city`, `created_by`, and `password`.

The endpoint returns the id of the resulting team that was created.

GET /teams/

This endpoint returns a list of teams. For each team it returns:

* `team_id`: The internal id of the team. Can be used to query the /teams/{team_id} endpoint.
* `created_by`: The user who created the team. Is null for real-life teams.
* `team_city`: The city the team is located in. Can be null for fictional teams.
* `team_name`: The name of the team.

You can filter for teams whose name contains a string by using the name or created by by using the
`name` and/or `created` query parameters.

You can sort the results by using the `sort` query parameter:
* `id` - Sort by team_id.
* `name` - Sort by team name alphabetically.

GET /games/{game_id}

This endpoint returns a game in 2022. It returns:
* `game_id`: The internal id of the team. Can be used to query the
  `/games/{game_id}` endpoint.
* `created_by`: The user who created the team. Is null for real-life games.
* `home_team_id`: The id of the home team. Can be used to query the `/teams/{team_id}` endpoint.
* `away_team_id`: The id of the away team. Can be used to query the `/teams/{team_id}` endpoint.
* `home_score`: The score of the home team.
* `away_score`: The score of the away team.

POST /game/

This endpoint takes in `created by`, `password`, and two lineup objects. A lineup consists of:
* `team_id`: The internal id of the team. Can be used to query the `/view_roster/{team_id}` endpoint.
* `lineup`: A list of exactly 10 player_ids (0 is the designated hitter, 1-9 are in batting order).

This endpoint returns a simulated game object. This game object calculates a random game based on a
player’s given stats. This consists of:
* `game_id`: The game id.
* `home_score`: The final score of the home team.
* `away_score`: The final score of the away team.
* `events`: A list of event objects that occurred in the game.

Each event is represented by a dictionary with the following keys:
* `inning`: The inning of the game.
* `T/B` Top/Bottom of inning.
* `player`: Player name of batter.
* `happening`: What the player did. Some examples include Walk, Strikeout, Home Run, etc.

POST /users/

This endpoint takes in a `username` and `password`. The player is represented
by a username and a password that is validated for user-level operations.

This function maintains unique usernames.

The endpoint returns the username of the resulting user that was created.

---
### Edge Cases:

The `play_simulation` endpoint will introduce some noise function for rookie players. This is because we need some variance in order to create a fair game. A player who maybe has only gone up at bat once and hit will have a batting average of 1.0, which would skew playing data.

Input will be validated for self-created characters. An error will be returned for an invalid character (more hits than at-bats, for example). Additional input validation means on a lineup to play a game, there must be exactly 10 players, and each field position must be covered, or an error is returned.

---
### Data gathered from:
https://www.kaggle.com/datasets/vivovinco/2022-mlb-player-stats?resource=download

https://www.retrosheet.org

![meme in questionable taste](./ballin.jpg?raw=true)

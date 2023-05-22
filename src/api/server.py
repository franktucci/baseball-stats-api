from fastapi import FastAPI
from src.api import players, teams, games, users, pkg_util

description = """
Baseball API. TBA

## Players

You can:
* **Lookup information on Players**

## Teams

You can:
* **Lookup information on Teams**

## Games
* **Play a simulated game**
"""

tags_metadata = [
    {
        "name": "players",
        "description": "Access information on players.",
    },
    {
        "name": "teams",
        "description": "Access information on teams.",
    },
    {
        "name": "games",
        "description": "Play a simulated game."
    },
    {
        "name": "users",
        "description": "Add a user."
    }
]

app = FastAPI(
    title="Baseball API",
    description=description,
    version="0.0.1",
    contact={
        "name": "Randall Caler and Frank Tucci",
        "email": "rcaler@calpoly.edu, ftucci@calpoly.edu",
    },
    openapi_tags=tags_metadata,
)

app.include_router(games.router)
app.include_router(players.router)
app.include_router(teams.router)
app.include_router(users.router)
app.include_router(pkg_util.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Baseball Stats API. See /docs for more information."}

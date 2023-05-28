from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query
from sqlalchemy import create_engine
import os
import dotenv
import sqlalchemy
from pydantic import BaseModel
from typing import List
from Crypto.Hash import SHA256

router = APIRouter()

class UserJson(BaseModel):
    username: str
    password: str

@router.post("/users/", tags=["users"])
def add_user(user: UserJson):
    """
    This endpoint takes in a `username` and `password`. The player is represented
    by a username and a password that is validated for user-level operations (Please don't input, like,
    your actual bank password here)

    This function maintains unique usernames.

    The endpoint returns the username of the resulting user that was created.
    """

    stmt = (sqlalchemy.select(db.users.c.username)).where(db.users.c.username == user.username)
    with db.engine.connect() as conn:
        user_result = conn.execute(stmt)
    if user_result.first() is not None:
        raise HTTPException(status_code=422, detail="username already exists.")

    d = SHA256.new()
    d.update(bytes(user.password, 'utf8'))

    with db.engine.begin() as conn:
        conn.execute(
            db.users.insert().values(
                username=user.username,
                password_hash=d.hexdigest()
            )
        )
    return {'username': user.username}

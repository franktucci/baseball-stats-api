from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy
from pydantic import BaseModel
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


class DeleteUserJson(BaseModel):
    password: str
@router.delete("/users/{username}", tags=["users"])
def delete_user(username: str, password: DeleteUserJson):
    """
    This endpoint deletes a user. It takes in a `password`.

    The endpoint returns the id of the resulting user that was deleted.
    """
    stmt = (
        sqlalchemy.select(
            db.users.c.password_hash
        )
        .where(db.users.c.username == username)
    )
    with db.engine.begin() as conn:
        user_result = conn.execute(stmt)

    user = user_result.first()
    if user is None:
        raise HTTPException(status_code=404, detail="user not found.")

    d = SHA256.new()
    d.update(bytes(password.password, 'utf8'))

    if d.hexdigest() != user.password_hash:
        raise HTTPException(status_code=422, detail="incorrect password.")

    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.delete(db.users).where(db.users.c.username == username))

    return {'username': username}

import csv
from src.datatypes import Player
import os
import io
from supabase import Client, create_client
import dotenv
from sqlalchemy import create_engine
import os
import dotenv
import sqlalchemy
import dotenv
import urllib.parse

dotenv.load_dotenv()
def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = urllib.parse.quote_plus(os.environ.get("POSTGRES_PASSWORD"))
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())
metadata_obj = sqlalchemy.MetaData()

players = sqlalchemy.Table("players", metadata_obj, autoload_with=engine)
teams = sqlalchemy.Table("teams", metadata_obj, autoload_with=engine)
games = sqlalchemy.Table("games", metadata_obj, autoload_with=engine)
events = sqlalchemy.Table("events", metadata_obj, autoload_with=engine)

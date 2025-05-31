import logging

import dotenv

# from pydantic import BaseModel
from pydantic_settings import BaseSettings  # , SettingsConfigDict

# import os


ENV_FILE = dotenv.find_dotenv()

logger = logging.getLogger(__name__)


class Kafka(BaseSettings):
    host: str = "localhost"
    port: int = 9094
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"


class ClickHouse(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

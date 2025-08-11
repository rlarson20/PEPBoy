from typing import Literal
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_url: str  # TODO: default to SQLite file
    env: Literal["dev"] | Literal["test"] | Literal["prod"] = "dev"
    # needs to get imported

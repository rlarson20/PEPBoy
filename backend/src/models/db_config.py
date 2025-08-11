from typing import Literal
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_url: str = "sqlite://./PEPBoy.db"
    env: Literal["dev", "test", "prod"] = "dev"
    # sqlite specifics
    sqlite_synchronous: str = "NORMAL" #find options and make this literal
    sqlite_journal_mode: str = "WAL" #find options and make this literal
    sqlite_cache_size: int: -64000 #MB cache

    class Config:
        env_file = ".env"
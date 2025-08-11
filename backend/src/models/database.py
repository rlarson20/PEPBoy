from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
import sqlite3

from .db_config import DatabaseSettings
from .orm_models import Base

settings = DatabaseSettings()

# SQLite optimizations for read-heavy workloads
def set_sqlite_pragma(dbapi_connection, connection_record):
    if 'sqlite' in settings.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute(f"PRAGMA synchronous = {settings.sqlite_synchronous}")
        cursor.execute(f"PRAGMA journal_mode = {settings.sqlite_journal_mode}")
        cursor.execute(f"PRAGMA cache_size = {settings.sqlite_cache_size}")
        cursor.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        cursor.close()

# Create engine
if settings.env == "test":
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )

# Apply SQLite optimizations
if "sqlite" in settings.database_url:
    event.listen(engine, "connect", set_sqlite_pragma)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
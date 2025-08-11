# backend/tests/conftest.py (future)
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.orm_models import Base


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

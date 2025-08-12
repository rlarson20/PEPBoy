"""
Comprehensive test fixtures for PEPBoy backend testing.

This module provides shared fixtures used across all test modules,
including database setup, mock data, and utility functions.
"""

import asyncio
import os
import tempfile
from datetime import date, datetime
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio
from faker import Faker
from freezegun import freeze_time
from httpx import AsyncClient, Response
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from src.models.orm_models import Author, Base, PEP


# =============================================================================
# Session Scope Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def fake() -> Faker:
    """Provide a Faker instance for generating test data."""
    Faker.seed(12345)  # Ensure reproducible test data
    return Faker()


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture
def test_db_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for SQL debugging
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a database session for testing with automatic rollback."""
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest_asyncio.fixture
async def async_test_db_engine():
    """Create an async in-memory SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_test_db_session(
    async_test_db_engine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create an async database session for testing with automatic rollback."""
    AsyncSessionLocal = async_sessionmaker(
        bind=async_test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


# =============================================================================
# Model Fixtures
# =============================================================================

@pytest.fixture
def sample_author(fake: Faker) -> Author:
    """Create a sample Author instance for testing."""
    return Author(
        id=fake.random_int(min=1, max=1000),
        name=fake.name(),
    )


@pytest.fixture
def sample_pep(fake: Faker) -> PEP:
    """Create a sample PEP instance for testing."""
    return PEP(
        number=fake.random_int(min=1, max=999),
        title=fake.sentence(nb_words=6),
        discussions_to=fake.email(),
        status=fake.random_element(elements=("Draft", "Final", "Accepted", "Rejected")),
        type=fake.random_element(elements=("Standards Track", "Informational", "Process")),
        topic=fake.random_element(elements=("Core", "Library", "Typing")),
        created=fake.date_between(start_date="-10y", end_date="today"),
        python_version=fake.random_element(elements=("3.9", "3.10", "3.11", "3.12")),
        post_history=fake.text(max_nb_chars=200),
        resolution=fake.url(),
        requires=None,
        replaces=None,
        superseded_by=None,
        url=fake.url(),
    )


@pytest.fixture
def sample_pep_with_authors(
    sample_pep: PEP, sample_author: Author, fake: Faker
) -> PEP:
    """Create a sample PEP with associated authors."""
    additional_author = Author(
        id=fake.random_int(min=1001, max=2000), name=fake.name()
    )
    sample_pep.authors = [sample_author, additional_author]
    return sample_pep


# =============================================================================
# HTTP Client Fixtures
# =============================================================================

@pytest.fixture
def mock_httpx_response() -> Mock:
    """Create a mock HTTPX response for testing."""
    response = Mock(spec=Response)
    response.status_code = 200
    response.json.return_value = {
        "1": {
            "number": 1,
            "title": "PEP Purpose and Guidelines",
            "authors": ["Barry Warsaw", "Jeremy Hylton"],
            "discussions_to": "python-dev@python.org",
            "status": "Active",
            "type": "Process",
            "topic": "Core",
            "created": "2000-06-13",
            "python_version": None,
            "post_history": "",
            "resolution": None,
            "requires": None,
            "replaces": None,
            "superseded_by": None,
            "url": "https://peps.python.org/pep-0001/",
        }
    }
    return response


@pytest.fixture
def mock_httpx_client(mock_httpx_response: Mock):
    """Create a mock HTTPX client with predefined responses."""
    with patch("httpx.get") as mock_get:
        mock_get.return_value = mock_httpx_response
        yield mock_get


# =============================================================================
# Time and Environment Fixtures
# =============================================================================

@pytest.fixture
def frozen_time():
    """Freeze time for consistent testing of time-dependent code."""
    with freeze_time("2024-01-15 12:00:00"):
        yield


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_env_vars():
    """Set up test environment variables."""
    original_env = dict(os.environ)
    
    # Set test-specific environment variables
    test_vars = {
        "TESTING": "true",
        "DATABASE_URL": "sqlite:///test.db",
        "LOG_LEVEL": "DEBUG",
    }
    
    for key, value in test_vars.items():
        os.environ[key] = value
    
    yield test_vars
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def assert_model_equality():
    """Utility function to assert model equality with detailed error messages."""
    
    def _assert_equality(model1, model2, exclude_fields=None):
        """
        Assert that two model instances are equal.
        
        Args:
            model1: First model instance
            model2: Second model instance
            exclude_fields: List of field names to exclude from comparison
        """
        exclude_fields = exclude_fields or []
        
        assert type(model1) == type(model2), f"Model types don't match: {type(model1)} != {type(model2)}"
        
        for field in model1.__table__.columns.keys():
            if field in exclude_fields:
                continue
                
            value1 = getattr(model1, field)
            value2 = getattr(model2, field)
            
            assert value1 == value2, f"Field '{field}' doesn't match: {value1} != {value2}"
    
    return _assert_equality


@pytest.fixture
def db_reset():
    """Fixture to reset database state between tests."""
    
    def _reset_db(session: Session):
        """Reset database by deleting all records."""
        # Delete in reverse order to respect foreign key constraints
        session.query(PEP).delete()
        session.query(Author).delete()
        session.commit()
    
    return _reset_db


# =============================================================================
# API Testing Fixtures
# =============================================================================

@pytest_asyncio.fixture
async def test_client():
    """Create a test client for API testing."""
    # This would typically import your FastAPI app
    # from src.main import app
    # 
    # async with AsyncClient(app=app, base_url="http://test") as client:
    #     yield client
    
    # For now, provide a mock client
    mock_client = Mock(spec=AsyncClient)
    yield mock_client


# =============================================================================
# Test Data Collections
# =============================================================================

@pytest.fixture
def sample_pep_data(fake: Faker) -> dict:
    """Create sample PEP data as a dictionary."""
    return {
        "number": fake.random_int(min=1, max=999),
        "title": fake.sentence(nb_words=6),
        "authors": [fake.name() for _ in range(fake.random_int(min=1, max=3))],
        "discussions_to": fake.email(),
        "status": fake.random_element(elements=("Draft", "Final", "Accepted")),
        "type": fake.random_element(elements=("Standards Track", "Informational")),
        "topic": "Core",
        "created": fake.date_between(start_date="-5y", end_date="today").isoformat(),
        "python_version": fake.random_element(elements=("3.9", "3.10", "3.11")),
        "url": fake.url(),
    }


@pytest.fixture
def multiple_peps_data(fake: Faker) -> list[dict]:
    """Create multiple sample PEP data entries."""
    return [
        {
            "number": i,
            "title": fake.sentence(nb_words=6),
            "authors": [fake.name()],
            "status": fake.random_element(elements=("Draft", "Final", "Accepted")),
            "type": "Standards Track",
            "topic": "Core",
            "created": fake.date_between(start_date="-2y", end_date="today").isoformat(),
            "url": f"https://peps.python.org/pep-{i:04d}/",
        }
        for i in range(1, 6)
    ]


# =============================================================================
# Performance Testing Fixtures
# =============================================================================

@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests."""
    import time
    
    class PerformanceTracker:
        def __init__(self):
            self.start_time = None
            self.measurements = {}
        
        def start(self, name: str = "default"):
            self.start_time = time.perf_counter()
            return self
        
        def stop(self, name: str = "default", max_duration: float | None = None):
            if self.start_time is None:
                raise ValueError("Timer not started")
            
            duration = time.perf_counter() - self.start_time
            self.measurements[name] = duration
            
            if max_duration and duration > max_duration:
                raise AssertionError(
                    f"Operation '{name}' took {duration:.3f}s, "
                    f"expected max {max_duration:.3f}s"
                )
            
            return duration
    
    return PerformanceTracker()

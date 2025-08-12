# Backend Testing Documentation

This directory contains comprehensive test suites for the PEPBoy backend application, implementing Test-Driven Development (TDD) methodology and best practices.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Test Configuration](#test-configuration)
- [Running Tests](#running-tests)
- [TDD Methodology](#tdd-methodology)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Test Fixtures and Factories](#test-fixtures-and-factories)
- [Performance Testing](#performance-testing)
- [Coverage Requirements](#coverage-requirements)

## Directory Structure

```
backend/tests/
├── README.md                 # This file
├── conftest.py              # Shared test fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── test_models.py       # ORM model tests
│   ├── test_pep_repository.py # Repository pattern tests
│   └── test_data_fetcher.py # Data fetching service tests
├── integration/             # Integration tests
├── fixtures/                # Test data and factories
│   ├── __init__.py
│   └── factories.py         # Factory Boy factories
└── utils/                   # Test utilities and helpers
    └── __init__.py
```

## Test Configuration

### pytest.ini

The project uses pytest with the following key configurations:

- **Test Discovery**: Automatically finds tests matching `test_*.py` or `*_test.py`
- **Coverage**: Minimum 85% coverage requirement
- **Async Support**: Full asyncio testing support
- **Markers**: Categorized tests (unit, integration, slow, external, etc.)

### Dependencies

Key testing dependencies (defined in `pyproject.toml`):

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.4.1",
    "pytest-asyncio>=1.1.0",
    "pytest-cov>=6.2.1",
    "factory-boy>=3.3.0",
    "faker>=20.1.0",
    "freezegun>=1.4.0",
    "httpx>=0.25.0",
]
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m slow

# Run tests in verbose mode
pytest -v

# Run tests in parallel
pytest -n auto  # Requires pytest-xdist
```

### Test Categories

Use markers to run specific categories:

```bash
# Unit tests only
pytest -m "unit"

# Integration tests only  
pytest -m "integration"

# Fast tests (exclude slow tests)
pytest -m "not slow"

# Database tests
pytest -m "database"

# External service tests (usually skipped)
pytest -m "external"
```

### Environment Setup

```bash
# Install test dependencies
pip install -e ".[test]"

# Set test environment variables
export TESTING=true
export DATABASE_URL=sqlite:///test.db
```

## TDD Methodology

This project follows the **Red-Green-Refactor** cycle:

### 1. Red Phase
Write a failing test that defines the desired behavior:

```python
def test_pep_creation_success(self, test_db_session: Session):
    """Test successful creation of a PEP instance."""
    # Arrange
    pep_data = {
        "number": 1,
        "title": "PEP Purpose and Guidelines",
        "status": "Active",
        # ... other fields
    }
    
    # Act
    pep = PEP(**pep_data)
    test_db_session.add(pep)
    test_db_session.commit()
    
    # Assert
    assert pep.number == 1
    assert pep.title == "PEP Purpose and Guidelines"
```

### 2. Green Phase
Write minimal code to make the test pass:

```python
class PEP(Base):
    __tablename__ = "peps"
    
    number: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String(20))
    # ... minimal implementation
```

### 3. Refactor Phase
Improve the code while keeping tests green:

```python
class PEP(Base):
    """SQLAlchemy model for a Python Enhancement Proposal (PEP)."""
    
    __tablename__ = "peps"
    
    # Add validation, relationships, methods, etc.
    number: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    # ... enhanced implementation
```

## Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation:

- **Models** (`test_models.py`): ORM model validation, relationships, business logic
- **Repository** (`test_pep_repository.py`): Data access layer, queries, pagination
- **Services** (`test_data_fetcher.py`): Business logic, external API interactions

**Example Unit Test Structure:**

```python
class TestPEPModel:
    """Test cases for the PEP model."""
    
    def test_pep_creation_success(self, test_db_session):
        """Test successful PEP creation."""
        # Test implementation
        
    def test_pep_validation_errors(self, test_db_session):
        """Test PEP validation failures."""
        # Test implementation
        
    def test_pep_relationships(self, test_db_session):
        """Test PEP-Author relationships."""
        # Test implementation
```

### Integration Tests (`tests/integration/`)

Test component interactions:

- API endpoint testing
- Database integration testing
- External service integration

### Performance Tests

Tests marked with `@pytest.mark.slow`:

```python
@pytest.mark.slow
def test_bulk_operations_performance(self, performance_tracker):
    """Test performance of bulk operations."""
    with performance_tracker.start():
        # Perform bulk operation
        pass
    
    duration = performance_tracker.stop(max_duration=2.0)
    assert duration < 2.0
```

## Writing Tests

### Test Structure Guidelines

Follow the **Arrange-Act-Assert** pattern:

```python
def test_example_function():
    # Arrange: Set up test data and conditions
    input_data = {"key": "value"}
    expected_result = "expected_output"
    
    # Act: Execute the function under test
    result = function_under_test(input_data)
    
    # Assert: Verify the results
    assert result == expected_result
```

### Naming Conventions

- Test files: `test_*.py`
- Test classes: `TestClassName`
- Test methods: `test_what_it_does_when_condition`

**Examples:**
```python
def test_pep_creation_success()
def test_pep_creation_with_invalid_number_raises_error()
def test_repository_get_pep_returns_none_when_not_found()
```

### Test Documentation

Include docstrings explaining:
- What behavior is being tested
- TDD phase (Red/Green/Refactor notes)
- Edge cases or special conditions

```python
def test_pep_unique_constraint(self, test_db_session):
    """Test that PEP numbers must be unique.
    
    TDD Red: Write test expecting constraint violation
    TDD Green: Add unique constraint to model
    TDD Refactor: Add proper error handling
    """
```

## Test Fixtures and Factories

### Using Fixtures (`conftest.py`)

Common fixtures available in all tests:

```python
def test_example(test_db_session, sample_pep, fake):
    """Example test using fixtures."""
    # test_db_session: Database session with automatic cleanup
    # sample_pep: Pre-created PEP instance
    # fake: Faker instance for generating test data
```

### Using Factory Boy (`fixtures/factories.py`)

Create test data with factories:

```python
def test_with_factory():
    # Create single instance
    pep = PEPFactory.build()
    
    # Create with overrides
    pep = PEPFactory.build(number=123, title="Custom Title")
    
    # Create batch
    peps = BatchFactory.create_pep_collection(size=10)
    
    # Create with relationships
    pep_with_authors = PEPWithAuthorsFactory.build()
```

### Available Factories

- `AuthorFactory`: Creates Author instances
- `PEPFactory`: Creates basic PEP instances  
- `PEPWithAuthorsFactory`: Creates PEPs with associated authors
- `DraftPEPFactory`: Creates PEPs with Draft status
- `FinalPEPFactory`: Creates PEPs with Final status
- `BatchFactory`: Utility for creating collections

## Performance Testing

### Performance Tracking

Use the `performance_tracker` fixture:

```python
def test_query_performance(self, repository, performance_tracker):
    """Test that queries complete within acceptable time."""
    
    with performance_tracker.start():
        results = repository.list_all_peps(limit=100)
    
    duration = performance_tracker.stop(max_duration=1.0)
    
    assert len(results) == 100
    assert duration < 1.0  # Should complete within 1 second
```

### Performance Test Guidelines

- Mark slow tests: `@pytest.mark.slow`
- Set reasonable time limits
- Test with realistic data volumes
- Consider database optimization

## Coverage Requirements

### Minimum Coverage

- **Line Coverage**: 85% minimum
- **Branch Coverage**: 85% minimum
- **Function Coverage**: 85% minimum

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Terminal coverage report
pytest --cov=src --cov-report=term-missing
```

### Coverage Configuration

Exclusions defined in `pytest.ini`:

- Test files themselves
- Configuration files
- Migration files
- Development utilities

## Continuous Integration

### Test Pipeline

Tests run automatically on:

- Pull requests
- Main branch commits
- Release builds

### Required Checks

- All tests pass
- Coverage thresholds met
- No linting errors
- Type checking passes

## Best Practices

### Test Independence

- Each test should be independent
- Use database transactions/rollback
- Clean up resources in fixtures
- Avoid test order dependencies

### Mock External Dependencies

```python
@patch('src.services.data_fetcher.httpx.get')
def test_api_call_success(self, mock_get):
    """Test successful API call."""
    mock_get.return_value = Mock(status_code=200, json=lambda: {...})
    # Test implementation
```

### Error Testing

Test both success and failure scenarios:

```python
def test_success_case(self):
    """Test normal operation."""
    
def test_handles_network_error(self):
    """Test graceful handling of network failures."""
    
def test_validates_input_parameters(self):
    """Test input validation and error messages."""
```

### Async Testing

For async code, use `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function(self, async_test_db_session):
    """Test async database operations."""
    async with async_test_db_session as session:
        result = await async_function(session)
        assert result is not None
```

## Debugging Tests

### Running Single Tests

```bash
# Run specific test method
pytest tests/unit/test_models.py::TestPEPModel::test_pep_creation_success

# Run with debugging
pytest --pdb tests/unit/test_models.py

# Run with print statements
pytest -s tests/unit/test_models.py
```

### Test Debugging Tips

- Use `pytest.set_trace()` for breakpoints
- Add `print()` statements for debugging (use `-s` flag)
- Check fixture values with `--setup-show`
- Use `--tb=long` for detailed tracebacks

## Contributing

When adding new tests:

1. Follow TDD methodology
2. Include both positive and negative test cases
3. Add appropriate markers
4. Document complex test scenarios
5. Ensure good coverage of new code
6. Update this README if adding new patterns

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [TDD Best Practices](https://testdriven.io/blog/modern-tdd/)
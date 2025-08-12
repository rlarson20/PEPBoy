# PEPBoy Test-Driven Development Architecture Design

## Executive Summary

This document provides a comprehensive Test-Driven Development (TDD) strategy and architecture for the PEPBoy web application. The design addresses testing for both backend (FastAPI/SQLAlchemy) and frontend (React/TypeScript) components, establishing a robust foundation for quality assurance, maintainability, and continuous development.

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Test Framework Architecture](#test-framework-architecture)
3. [Directory Structure](#directory-structure)
4. [Testing Strategies](#testing-strategies)
5. [Framework Configurations](#framework-configurations)
6. [TDD Methodology](#tdd-methodology)
7. [Test Infrastructure](#test-infrastructure)
8. [CI/CD Integration](#cicd-integration)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Current State Analysis

### Backend Status
- **Framework**: FastAPI with SQLAlchemy 2.0
- **Current Testing**: Minimal (`conftest.py` exists, pytest in dependencies)
- **Issues**: Syntax errors in `populate_db.py`, incomplete implementation
- **Strengths**: Repository pattern, Pydantic models, proper separation of concerns

### Frontend Status
- **Framework**: React 19 with TypeScript
- **Current Testing**: None (no test infrastructure)
- **Issues**: Placeholder components, incomplete API integration
- **Strengths**: TypeScript for type safety, clean component structure

### Critical Gaps
1. No comprehensive test coverage
2. Missing test infrastructure setup
3. No authentication testing strategy
4. Lack of integration testing
5. No end-to-end testing framework
6. Missing mock data and fixtures

---

## Test Framework Architecture

### Backend Testing Stack

#### Core Framework
- **Primary**: `pytest` (already included)
- **Async Testing**: `pytest-asyncio`
- **Coverage**: `pytest-cov`
- **HTTP Testing**: `httpx` (for FastAPI testing)
- **Database Testing**: `pytest-alembic`, `sqlalchemy-utils`

#### Additional Tools
- **Mocking**: `unittest.mock` + `pytest-mock`
- **Fixtures**: `factory-boy` for test data generation
- **Performance**: `pytest-benchmark`
- **Parallel Testing**: `pytest-xdist`

#### Testing Types
```
Backend Testing Pyramid:
┌─────────────────────────┐
│     E2E Tests (5%)      │ ← Full API workflows
├─────────────────────────┤
│  Integration Tests (20%)│ ← API + Database
├─────────────────────────┤
│   Unit Tests (75%)      │ ← Models, Services, Utils
└─────────────────────────┘
```

### Frontend Testing Stack

#### Core Framework
- **Primary**: `Vitest` (faster than Jest, better Vite integration)
- **Component Testing**: `@testing-library/react`
- **User Event Testing**: `@testing-library/user-event`
- **DOM Testing**: `@testing-library/jest-dom`

#### Additional Tools
- **Mocking**: `MSW` (Mock Service Worker) for API mocking
- **Coverage**: `@vitest/coverage-v8`
- **Visual Testing**: `@storybook/test-runner` (future enhancement)
- **Accessibility**: `@testing-library/jest-dom` with a11y matchers

#### Testing Types
```
Frontend Testing Pyramid:
┌─────────────────────────┐
│     E2E Tests (5%)      │ ← User journeys
├─────────────────────────┤
│  Integration Tests (25%)│ ← Component + API
├─────────────────────────┤
│   Unit Tests (70%)      │ ← Components, Utils, Hooks
└─────────────────────────┘
```

### End-to-End Testing

#### Framework Selection
- **Primary**: `Playwright` (cross-browser, reliable, fast)
- **Alternative**: `Cypress` (developer-friendly, but single-browser)

#### E2E Strategy
- User journey testing
- Critical path validation
- Cross-browser compatibility
- Visual regression testing

---

## Directory Structure

### Backend Test Structure
```
backend/
├── tests/
│   ├── conftest.py                 # Global fixtures
│   ├── pytest.ini                 # Pytest configuration
│   ├── unit/
│   │   ├── models/
│   │   │   ├── test_orm_models.py
│   │   │   └── test_pydantic_models.py
│   │   ├── services/
│   │   │   ├── test_pep_repository.py
│   │   │   ├── test_content_processor.py
│   │   │   └── test_data_fetcher.py
│   │   ├── tasks/
│   │   │   ├── test_content_parsing.py
│   │   │   ├── test_generate_index.py
│   │   │   └── test_populate_db.py
│   │   └── utils/
│   │       └── test_helpers.py
│   ├── integration/
│   │   ├── test_api_endpoints.py
│   │   ├── test_database_operations.py
│   │   ├── test_auth_workflows.py
│   │   └── test_search_functionality.py
│   ├── fixtures/
│   │   ├── pep_data.py
│   │   ├── test_database.py
│   │   └── mock_responses.py
│   └── utils/
│       ├── test_helpers.py
│       ├── assertions.py
│       └── factories.py
```

### Frontend Test Structure
```
frontend/
├── src/
│   ├── __tests__/
│   │   ├── setup.ts               # Test environment setup
│   │   └── utils/
│   │       ├── test-utils.tsx     # Custom render functions
│   │       ├── mock-api.ts        # MSW setup
│   │       └── fixtures.ts        # Test data
│   ├── components/
│   │   ├── Header/
│   │   │   ├── Header.tsx
│   │   │   ├── Header.test.tsx
│   │   │   └── Header.stories.tsx
│   │   ├── SearchBar/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchBar.test.tsx
│   │   │   └── SearchBar.stories.tsx
│   │   └── ...
│   ├── services/
│   │   ├── api.ts
│   │   └── api.test.ts
│   ├── hooks/
│   │   ├── usePEPData.ts
│   │   └── usePEPData.test.ts
│   └── utils/
│       ├── helpers.ts
│       └── helpers.test.ts
├── vitest.config.ts
└── vitest.workspace.ts
```

### E2E Test Structure
```
e2e/
├── tests/
│   ├── user-journeys/
│   │   ├── browse-peps.spec.ts
│   │   ├── search-functionality.spec.ts
│   │   └── pep-details.spec.ts
│   ├── auth/ (future)
│   │   ├── login.spec.ts
│   │   ├── logout.spec.ts
│   │   └── permissions.spec.ts
│   └── api/
│       ├── pep-endpoints.spec.ts
│       └── search-endpoints.spec.ts
├── fixtures/
│   ├── test-data.json
│   └── mock-server.ts
├── utils/
│   ├── page-objects/
│   │   ├── HomePage.ts
│   │   ├── SearchPage.ts
│   │   └── PEPDetailPage.ts
│   └── helpers.ts
├── playwright.config.ts
└── package.json
```

---

## Testing Strategies

### Unit Testing Strategy

#### Backend Unit Tests

**Models Testing**
```python
# Example: test_orm_models.py
def test_pep_model_creation():
    """Test PEP model instantiation and validation."""
    pep = PEP(
        number=42,
        title="Test PEP",
        status="Draft",
        type="Standards Track",
        topic="Core",
        url="https://peps.python.org/pep-0042/"
    )
    assert pep.number == 42
    assert pep.title == "Test PEP"

def test_pep_author_relationship():
    """Test many-to-many relationship between PEPs and Authors."""
    # Test relationship creation and queries
```

**Repository Testing**
```python
# Example: test_pep_repository.py
def test_get_pep_by_number(test_db, sample_pep):
    """Test retrieving PEP by number."""
    repo = PEPRepository(test_db)
    pep = repo.get_pep_by_number(42)
    assert pep.number == 42

def test_search_peps_by_title(test_db, sample_peps):
    """Test title-based search functionality."""
    repo = PEPRepository(test_db)
    results = repo.search_peps_by_title("typing")
    assert len(results) > 0
```

**Service Layer Testing**
```python
# Example: test_content_processor.py
def test_sanitize_content():
    """Test content sanitization for security."""
    processor = ContentProcessor()
    malicious_input = "<script>alert('xss')</script>"
    clean_output = processor.sanitize(malicious_input)
    assert "<script>" not in clean_output
```

#### Frontend Unit Tests

**Component Testing**
```typescript
// Example: SearchBar.test.tsx
describe('SearchBar', () => {
  it('renders search input correctly', () => {
    render(<SearchBar onSearch={mockOnSearch} />);
    expect(screen.getByPlaceholderText(/search peps/i)).toBeInTheDocument();
  });

  it('calls onSearch when form is submitted', async () => {
    const mockOnSearch = vi.fn();
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const searchInput = screen.getByRole('textbox');
    const submitButton = screen.getByRole('button');
    
    await userEvent.type(searchInput, 'typing');
    await userEvent.click(submitButton);
    
    expect(mockOnSearch).toHaveBeenCalledWith('typing');
  });
});
```

**Service Testing**
```typescript
// Example: api.test.ts
describe('API Service', () => {
  beforeEach(() => {
    server.resetHandlers();
  });

  it('fetches PEP list successfully', async () => {
    const mockPeps = [{ number: 1, title: 'Test PEP' }];
    server.use(
      http.get('/api/peps', () => {
        return HttpResponse.json({ peps: mockPeps, total: 1 });
      })
    );

    const result = await fetchPeps();
    expect(result.peps).toEqual(mockPeps);
  });
});
```

### Integration Testing Strategy

#### API Integration Tests
```python
# Example: test_api_endpoints.py
async def test_get_peps_endpoint(client, sample_peps):
    """Test GET /api/peps endpoint with pagination."""
    response = await client.get("/api/peps?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "peps" in data
    assert "total" in data
    assert len(data["peps"]) <= 10

async def test_search_endpoint(client, sample_peps):
    """Test search functionality via API."""
    response = await client.get("/api/search?q=typing")
    assert response.status_code == 200
    results = response.json()
    assert all("typing" in pep["title"].lower() for pep in results["peps"])
```

#### Database Integration Tests
```python
# Example: test_database_operations.py
def test_pep_creation_with_authors(db_session):
    """Test creating PEP with multiple authors."""
    pep = PEP(number=999, title="Test PEP", ...)
    author1 = Author(name="Test Author 1")
    author2 = Author(name="Test Author 2")
    
    pep.authors = [author1, author2]
    db_session.add(pep)
    db_session.commit()
    
    retrieved_pep = db_session.get(PEP, 999)
    assert len(retrieved_pep.authors) == 2
```

#### Frontend Integration Tests
```typescript
// Example: PEPList.integration.test.tsx
describe('PEP List Integration', () => {
  it('loads and displays PEPs from API', async () => {
    const mockPeps = [
      { number: 1, title: 'PEP 1', status: 'Final' },
      { number: 8, title: 'PEP 8', status: 'Active' }
    ];

    server.use(
      http.get('/api/peps', () => {
        return HttpResponse.json({ peps: mockPeps, total: 2 });
      })
    );

    render(<PEPList />);
    
    await waitFor(() => {
      expect(screen.getByText('PEP 1')).toBeInTheDocument();
      expect(screen.getByText('PEP 8')).toBeInTheDocument();
    });
  });
});
```

### End-to-End Testing Strategy

#### Critical User Journeys
```typescript
// Example: browse-peps.spec.ts
test('user can browse and view PEP details', async ({ page }) => {
  await page.goto('/');
  
  // Verify PEP list loads
  await expect(page.getByText('Python Enhancement Proposals')).toBeVisible();
  
  // Click on first PEP
  await page.getByText('PEP 1').first().click();
  
  // Verify detail page
  await expect(page.getByRole('heading', { name: /PEP 1/ })).toBeVisible();
  await expect(page.getByText('Final')).toBeVisible();
});

test('user can search for PEPs', async ({ page }) => {
  await page.goto('/');
  
  // Perform search
  await page.getByPlaceholder('Search PEPs').fill('typing');
  await page.getByRole('button', { name: 'Search' }).click();
  
  // Verify search results
  await expect(page.getByText('Search Results')).toBeVisible();
  await expect(page.getByText(/typing/i)).toBeVisible();
});
```

---

## Framework Configurations

### Backend Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    auth: Authentication related tests
asyncio_mode = auto
```

#### conftest.py Enhancement
```python
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app import app
from src.models.orm_models import Base
from src.models.database import get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_db():
    """Create test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()

@pytest.fixture
async def client(test_db):
    """Create test client."""
    app.dependency_overrides[get_db] = lambda: test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_pep(test_db):
    """Create sample PEP for testing."""
    from src.models.orm_models import PEP
    pep = PEP(
        number=42,
        title="Test PEP",
        status="Draft",
        type="Standards Track",
        topic="Core",
        url="https://peps.python.org/pep-0042/"
    )
    test_db.add(pep)
    test_db.commit()
    return pep
```

### Frontend Configuration

#### vitest.config.ts
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      exclude: [
        'node_modules/',
        'src/__tests__/',
        '**/*.stories.tsx',
        '**/*.test.{ts,tsx}',
        'src/main.tsx',
        'src/vite-env.d.ts'
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 80,
          statements: 80
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
```

#### Test Setup (setup.ts)
```typescript
import '@testing-library/jest-dom';
import { expect, afterEach, beforeAll, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';
import { server } from './utils/mock-api';

expect.extend(matchers);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterAll(() => server.close());
afterEach(() => {
  cleanup();
  server.resetHandlers();
});
```

#### MSW Setup (mock-api.ts)
```typescript
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

const handlers = [
  http.get('/api/peps', () => {
    return HttpResponse.json({
      peps: [
        { number: 1, title: 'PEP 1', status: 'Final' },
        { number: 8, title: 'PEP 8', status: 'Active' }
      ],
      total: 2,
      skip: 0,
      limit: 100
    });
  }),

  http.get('/api/peps/:number', ({ params }) => {
    const number = parseInt(params.number as string);
    return HttpResponse.json({
      number,
      title: `PEP ${number}`,
      status: 'Final',
      type: 'Standards Track',
      topic: 'Core',
      created: '2001-03-26',
      python_version: null,
      url: `https://peps.python.org/pep-${number.toString().padStart(4, '0')}/`,
      authors: [{ id: 1, name: 'Test Author' }]
    });
  }),

  http.get('/api/search', ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('q');
    return HttpResponse.json({
      peps: [
        { number: 484, title: 'Type Hints', status: 'Final' }
      ],
      total: 1,
      skip: 0,
      limit: 100
    });
  })
];

export const server = setupServer(...handlers);
```

### E2E Configuration

#### playwright.config.ts
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: [
    {
      command: 'npm run dev',
      port: 3000,
      cwd: '../frontend',
    },
    {
      command: 'uvicorn src.app:app --host 0.0.0.0 --port 8420',
      port: 8420,
      cwd: '../backend',
    }
  ],
});
```

---

## TDD Methodology

### Red-Green-Refactor Workflow

#### Phase 1: RED (Write Failing Test)
```python
# Example: Write failing test first
def test_create_pep_with_validation():
    """Test PEP creation with proper validation."""
    # This test will fail initially
    pep_data = {
        "number": 42,
        "title": "",  # Invalid: empty title
        "status": "Draft",
        "type": "Standards Track",
        "topic": "Core"
    }
    
    with pytest.raises(ValidationError):
        PEP(**pep_data)
```

#### Phase 2: GREEN (Make Test Pass)
```python
# Add validation to PEP model
from pydantic import validator

class PEP(Base):
    # ... existing fields ...
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

#### Phase 3: REFACTOR (Improve Code)
```python
# Extract validation logic to separate module
from .validators import validate_title, validate_pep_number

class PEP(Base):
    # ... fields ...
    
    @validator('title')
    def validate_title(cls, v):
        return validate_title(v)
    
    @validator('number')
    def validate_number(cls, v):
        return validate_pep_number(v)
```

### TDD Best Practices

#### Test Naming Convention
```python
# Pattern: test_[unit_under_test]_[scenario]_[expected_behavior]
def test_pep_repository_get_by_number_returns_pep_when_exists():
    pass

def test_pep_repository_get_by_number_returns_none_when_not_exists():
    pass

def test_search_service_by_title_filters_results_case_insensitive():
    pass
```

#### Test Structure (AAA Pattern)
```python
def test_search_peps_by_title():
    # Arrange
    repo = PEPRepository(test_db)
    create_sample_peps(test_db)
    search_term = "typing"
    
    # Act
    results = repo.search_peps_by_title(search_term)
    
    # Assert
    assert len(results) > 0
    assert all(search_term.lower() in pep.title.lower() for pep in results)
```

#### Frontend TDD Example
```typescript
// RED: Write failing test
describe('usePEPData hook', () => {
  it('should fetch PEPs on mount', async () => {
    const { result } = renderHook(() => usePEPData());
    
    await waitFor(() => {
      expect(result.current.peps).toHaveLength(2);
      expect(result.current.loading).toBe(false);
    });
  });
});

// GREEN: Implement hook
function usePEPData() {
  const [peps, setPeps] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchPeps().then(data => {
      setPeps(data.peps);
      setLoading(false);
    });
  }, []);
  
  return { peps, loading };
}

// REFACTOR: Add error handling and optimization
function usePEPData() {
  const [state, setState] = useState({
    peps: [],
    loading: true,
    error: null
  });
  
  useEffect(() => {
    const abortController = new AbortController();
    
    fetchPeps({ signal: abortController.signal })
      .then(data => setState({ peps: data.peps, loading: false, error: null }))
      .catch(error => setState({ peps: [], loading: false, error }));
    
    return () => abortController.abort();
  }, []);
  
  return state;
}
```

---

## Test Infrastructure

### Mock Data and Fixtures

#### Factory Pattern for Test Data
```python
# backend/tests/utils/factories.py
import factory
from datetime import date
from src.models.orm_models import PEP, Author

class AuthorFactory(factory.Factory):
    class Meta:
        model = Author
    
    id = factory.Sequence(lambda n: n)
    name = factory.Faker('name')

class PEPFactory(factory.Factory):
    class Meta:
        model = PEP
    
    number = factory.Sequence(lambda n: n)
    title = factory.Faker('sentence', nb_words=4)
    status = factory.Iterator(['Draft', 'Final', 'Rejected', 'Active'])
    type = factory.Iterator(['Standards Track', 'Informational', 'Process'])
    topic = factory.Iterator(['Core', 'Library', 'Packaging'])
    created = factory.Faker('date_object')
    url = factory.LazyAttribute(lambda obj: f"https://peps.python.org/pep-{obj.number:04d}/")
    
    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for author in extracted:
                self.authors.append(author)
        else:
            # Create default author
            author = AuthorFactory()
            self.authors.append(author)
```

#### Frontend Test Fixtures
```typescript
// frontend/src/__tests__/utils/fixtures.ts
export const mockPEP = {
  number: 484,
  title: 'Type Hints',
  status: 'Final',
  type: 'Standards Track',
  topic: 'Core',
  created: '2014-09-29',
  python_version: '3.5',
  url: 'https://peps.python.org/pep-0484/',
  authors: [
    { id: 1, name: 'Guido van Rossum' },
    { id: 2, name: 'Jukka Lehtosalo' }
  ]
};

export const mockPEPList = {
  peps: [mockPEP],
  total: 1,
  skip: 0,
  limit: 100
};

export const createMockPEP = (overrides = {}): PEP => ({
  ...mockPEP,
  ...overrides
});
```

### Custom Test Utilities

#### Backend Test Helpers
```python
# backend/tests/utils/test_helpers.py
from typing import List
from sqlalchemy.orm import Session
from src.models.orm_models import PEP, Author

def create_test_peps(db: Session, count: int = 5) -> List[PEP]:
    """Create multiple test PEPs."""
    peps = []
    for i in range(count):
        pep = PEP(
            number=i + 1,
            title=f"Test PEP {i + 1}",
            status="Draft",
            type="Standards Track",
            topic="Core",
            url=f"https://peps.python.org/pep-{i+1:04d}/"
        )
        db.add(pep)
        peps.append(pep)
    
    db.commit()
    return peps

def assert_pep_equals(actual: PEP, expected: dict):
    """Custom assertion for PEP objects."""
    assert actual.number == expected["number"]
    assert actual.title == expected["title"]
    assert actual.status == expected["status"]
    # Add more assertions as needed
```

#### Frontend Test Utilities
```typescript
// frontend/src/__tests__/utils/test-utils.tsx
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ReactElement } from 'react';

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <BrowserRouter>
      {children}
    </BrowserRouter>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };

// Custom matchers
export const expectToBeLoading = (element: HTMLElement) => {
  expect(element).toHaveAttribute('aria-busy', 'true');
};

export const expectToHaveError = (element: HTMLElement, message?: string) => {
  expect(element).toHaveAttribute('role', 'alert');
  if (message) {
    expect(element).toHaveTextContent(message);
  }
};
```

---

## Authentication Testing Strategy (Future-Ready)

### Backend Authentication Tests

#### JWT Token Testing
```python
# tests/integration/test_auth_workflows.py
import jwt
from datetime import datetime, timedelta

async def test_login_success_returns_valid_jwt(client, test_user):
    """Test successful login returns valid JWT token."""
    login_data = {
        "username": test_user.username,
        "password": "testpassword"
    }
    
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    assert "access_token" in token_data
    assert "token_type" in token_data
    
    # Verify JWT structure
    token = token_data["access_token"]
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert decoded["sub"] == test_user.username
    assert "exp" in decoded

async def test_protected_endpoint_requires_auth(client):
    """Test protected endpoints require authentication."""
    response = await client.get("/api/admin/peps")
    assert response.status_code == 401

async def test_protected_endpoint_with_valid_token(client, auth_headers):
    """Test protected endpoints work with valid token."""
    response = await client.get("/api/admin/peps", headers=auth_headers)
    assert response.status_code == 200
```

#### Permission Testing
```python
async def test_admin_only_endpoint_rejects_regular_user(client, user_auth_headers):
    """Test admin-only endpoints reject regular users."""
    response = await client.delete("/api/admin/peps/999", headers=user_auth_headers)
    assert response.status_code == 403

async def test_admin_endpoint_allows_admin_user(client, admin_auth_headers):
    """Test admin endpoints allow admin users."""
    response = await client.delete("/api/admin/peps/999", headers=admin_auth_headers)
    assert response.status_code == 204  # or appropriate success code
```

### Frontend Authentication Tests

#### Auth Context Testing
```typescript
// components/AuthProvider.test.tsx
describe('AuthProvider', () => {
  it('provides login functionality', async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    
    await act(async () => {
      await result.current.login('testuser', 'password');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({
      username: 'testuser',
      role: 'user'
    });
  });
  
  it('handles logout correctly', async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });
    
    // Login first
    await act(async () => {
      await result.current.login('testuser', 'password');
    });
    
    // Then logout
    await act(async () => {
      await result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });
});
```

#### Protected Route Testing
```typescript
// components/ProtectedRoute.test.tsx
describe('ProtectedRoute', () => {
  it('redirects to login when not authenticated', () => {
    render(
      <MemoryRouter initialEntries={['/admin']}>
        <AuthProvider>
          <Routes>
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            } />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );
    
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });
  
  it('renders protected content when authenticated', () => {
    const mockAuthContext = {
      isAuthenticated: true,
      user: { username: 'admin', role: 'admin' },
      login: vi.fn(),
      logout: vi.fn()
    };
    
    render(
      <MemoryRouter initialEntries={['/admin']}>
        <AuthContext.Provider value={mockAuthContext}>
          <Routes>
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </AuthContext.Provider>
      </MemoryRouter>
    );
    
    expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
  });
});
```

---

## Assertion Strategies and Verification Patterns

### Backend Assertion Patterns

#### Database State Assertions
```python
def test_pep_creation_persists_to_database(test_db):
    """Test PEP creation with database persistence verification."""
    # Arrange
    pep_data = {
        "number": 123,
        "title": "Test PEP for Persistence",
        "status": "Draft",
        "type": "Standards Track",
        "topic": "Core",
        "url": "https://peps.python.org/pep-0123/"
    }
    
    # Act
    pep = PEP(**pep_data)
    test_db.add(pep)
    test_db.commit()
    
    # Assert - Multiple verification strategies
    # 1. Direct object assertion
    assert pep.id is not None
    assert pep.number == 123
    
    # 2. Database query verification
    retrieved_pep = test_db.get(PEP, pep.id)
    assert retrieved_pep is not None
    assert retrieved_pep.title == "Test PEP for Persistence"
    
    # 3. Count verification
    total_peps = test_db.query(PEP).count()
    assert total_peps == 1
```

#### API Response Assertions
```python
async def test_api_response_structure_and_content(client):
    """Test API response follows expected structure."""
    response = await client.get("/api/peps/1")
    
    # Status code assertion
    assert response.status_code == 200
    
    # Response structure assertion
    data = response.json()
    required_fields = ["number", "title", "status", "type", "url", "authors"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Type assertions
    assert isinstance(data["number"], int)
    assert isinstance(data["title"], str)
    assert isinstance(data["authors"], list)
    
    # Business logic assertions
    assert data["number"] > 0
    assert len(data["title"]) > 0
    assert data["status"] in ["Draft", "Final", "Rejected", "Active"]
```

### Frontend Assertion Patterns

#### Component State Assertions
```typescript
describe('PEP List Component', () => {
  it('displays loading state initially', () => {
    render(<PEPList />);
    
    // Visual state assertions
    expect(screen.getByRole('status')).toHaveTextContent('Loading...');
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    
    // Accessibility assertions
    expect(screen.getByRole('status')).toHaveAttribute('aria-live', 'polite');
  });
  
  it('displays PEP data when loaded', async () => {
    const mockPeps = [
      { number: 1, title: 'PEP 1', status: 'Final' },
      { number: 8, title: 'PEP 8', status: 'Active' }
    ];
    
    server.use(
      http.get('/api/peps', () => {
        return HttpResponse.json({ peps: mockPeps, total: 2 });
      })
    );
    
    render(<PEPList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByRole('status')).not.toBeInTheDocument();
    });
    
    // Content assertions
    expect(screen.getByText('PEP 1')).toBeInTheDocument();
    expect(screen.getByText('PEP 8')).toBeInTheDocument();
    
    // Count assertions
    const pepItems = screen.getAllByRole('listitem');
    expect(pepItems).toHaveLength(2);
    
    // Link assertions
    expect(screen.getByRole('link', { name: /PEP 1/ })).toHaveAttribute(
      'href', '/pep/1'
    );
  });
});
```

#### Form Validation Assertions
```typescript
describe('Search Form Validation', () => {
  it('shows validation error for empty search', async () => {
    render(<SearchForm onSubmit={vi.fn()} />);
    
    const submitButton = screen.getByRole('button', { name: /search/i });
    await userEvent.click(submitButton);
    
    // Error state assertions
    const errorMessage = await screen.findByRole('alert');
    expect(errorMessage).toHaveTextContent('Search query is required');
    
    // Input state assertions
    const searchInput = screen.getByRole('textbox');
    expect(searchInput).toHaveAttribute('aria-invalid', 'true');
    expect(searchInput).toHaveAttribute('aria-describedby');
    
    // Focus assertions
    expect(searchInput).toHaveFocus();
  });
  
  it('submits valid search query', async () => {
    const mockOnSubmit = vi.fn();
    render(<SearchForm onSubmit={mockOnSubmit} />);
    
    const searchInput = screen.getByRole('textbox');
    const submitButton = screen.getByRole('button', { name: /search/i });
    
    await userEvent.type(searchInput, 'typing');
    await userEvent.click(submitButton);
    
    // Submission assertions
    expect(mockOnSubmit).toHaveBeenCalledTimes(1);
    expect(mockOnSubmit).toHaveBeenCalledWith('typing');
    
    // No error state
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });
});
```

### Custom Assertion Helpers

#### Backend Custom Assertions
```python
# backend/tests/utils/assertions.py
from typing import Dict, Any, List
from src.models.orm_models import PEP

def assert_pep_data_matches(pep: PEP, expected_data: Dict[str, Any]):
    """Custom assertion for PEP object data matching."""
    for field, expected_value in expected_data.items():
        actual_value = getattr(pep, field)
        assert actual_value == expected_value, (
            f"PEP.{field} mismatch: expected {expected_value}, got {actual_value}"
        )

def assert_pep_list_ordered_by_number(peps: List[PEP]):
    """Assert PEP list is ordered by number."""
    numbers = [pep.number for pep in peps]
    assert numbers == sorted(numbers), "PEPs should be ordered by number"

def assert_search_results_contain_term(peps: List[PEP], search_term: str):
    """Assert all search results contain the search term."""
    for pep in peps:
        assert search_term.lower() in pep.title.lower(), (
            f"PEP {pep.number} title '{pep.title}' does not contain '{search_term}'"
        )
```

#### Frontend Custom Assertions
```typescript
// frontend/src/__tests__/utils/custom-assertions.ts
import { screen } from '@testing-library/react';

export const assertLoadingState = (isLoading: boolean) => {
  if (isLoading) {
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  } else {
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
  }
};

export const assertErrorState = (errorMessage?: string) => {
  const errorElement = screen.getByRole('alert');
  expect(errorElement).toBeInTheDocument();
  
  if (errorMessage) {
    expect(errorElement).toHaveTextContent(errorMessage);
  }
};

export const assertPEPListItem = (pepNumber: number, title: string) => {
  const linkElement = screen.getByRole('link', { name: new RegExp(title, 'i') });
  expect(linkElement).toBeInTheDocument();
  expect(linkElement).toHaveAttribute('href', `/pep/${pepNumber}`);
  
  const listItem = linkElement.closest('[role="listitem"]');
  expect(listItem).toBeInTheDocument();
};

export const assertAccessibility = async (element: HTMLElement) => {
  // Check for common accessibility attributes
  if (element.tagName === 'BUTTON') {
    expect(element).not.toHaveAttribute('aria-disabled', 'true');
  }
  
  if (element.getAttribute('role') === 'textbox') {
    expect(element).toHaveAttribute('aria-label');
  }
  
  // Additional accessibility checks can be added here
};
```

---

## Error Handling Testing Strategy

### Backend Error Testing

#### Exception Handling Tests
```python
# tests/unit/test_error_handling.py
import pytest
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

async def test_duplicate_pep_number_raises_integrity_error(test_db):
    """Test database constraint enforcement."""
    # Create first PEP
    pep1 = PEP(number=42, title="First PEP", status="Draft", 
               type="Standards Track", topic="Core", url="http://example.com")
    test_db.add(pep1)
    test_db.commit()
    
    # Attempt to create duplicate
    pep2 = PEP(number=42, title="Duplicate PEP", status="Draft",
               type="Standards Track", topic="Core", url="http://example2.com")
    test_db.add(pep2)
    
    with pytest.raises(IntegrityError):
        test_db.commit()

async def test_api_handles_not_found_gracefully(client):
    """Test 404 handling for non-existent PEP."""
    response = await client.get("/api/peps/99999")
    
    assert response.status_code == 404
    error_data = response.json()
    assert "detail" in error_data
    assert "not found" in error_data["detail"].lower()

async def test_api_handles_invalid_input(client):
    """Test validation error handling."""
    invalid_data = {
        "number": "not-a-number",
        "title": "",
        "status": "InvalidStatus"
    }
    
    response = await client.post("/api/peps", json=invalid_data)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data
    assert isinstance(error_data["detail"], list)
```

#### Service Layer Error Tests
```python
# tests/unit/services/test_error_scenarios.py
def test_pep_repository_handles_database_connection_error(mock_db_session):
    """Test repository graceful degradation on DB errors."""
    # Mock database connection failure
    mock_db_session.execute.side_effect = ConnectionError("Database unavailable")
    
    repo = PEPRepository(mock_db_session)
    
    with pytest.raises(ServiceUnavailableError):
        repo.get_pep_by_number(1)

def test_content_processor_handles_malformed_data():
    """Test content processor with invalid input."""
    processor = ContentProcessor()
    
    malformed_data = {"incomplete": "data"}
    
    with pytest.raises(ValidationError) as exc_info:
        processor.process_pep_data(malformed_data)
    
    assert "missing required fields" in str(exc_info.value)
```

### Frontend Error Testing

#### Error Boundary Testing
```typescript
// components/ErrorBoundary.test.tsx
describe('ErrorBoundary', () => {
  it('catches and displays component errors', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };
    
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });
  
  it('provides error reporting functionality', () => {
    const mockReportError = vi.fn();
    const ThrowError = () => {
      throw new Error('Test error');
    };
    
    render(
      <ErrorBoundary onError={mockReportError}>
        <ThrowError />
      </ErrorBoundary>
    );
    
    expect(mockReportError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({ componentStack: expect.any(String) })
    );
  });
});
```

#### Network Error Testing
```typescript
// services/api.test.ts
describe('API Error Handling', () => {
  it('handles network timeout errors', async () => {
    server.use(
      http.get('/api/peps', () => {
        return new Response(null, { status: 408 });
      })
    );
    
    await expect(fetchPeps()).rejects.toThrow('Request timeout');
  });
  
  it('handles server errors with retry logic', async () => {
    let callCount = 0;
    server.use(
      http.get('/api/peps', () => {
        callCount++;
        if (callCount < 3) {
          return new Response(null, { status: 500 });
        }
        return HttpResponse.json({ peps: [], total: 0 });
      })
    );
    
    const result = await fetchPepsWithRetry();
    expect(result).toEqual({ peps: [], total: 0 });
    expect(callCount).toBe(3);
  });
  
  it('provides user-friendly error messages', async () => {
    server.use(
      http.get('/api/peps', () => {
        return HttpResponse.json(
          { detail: 'Database connection failed' },
          { status: 503 }
        );
      })
    );
    
    await expect(fetchPeps()).rejects.toThrow(
      'Service temporarily unavailable. Please try again later.'
    );
  });
});
```

#### Form Error Testing
```typescript
// components/SearchForm.test.tsx
describe('SearchForm Error Handling', () => {
  it('displays validation errors', async () => {
    render(<SearchForm onSubmit={vi.fn()} />);
    
    // Submit empty form
    await userEvent.click(screen.getByRole('button', { name: /search/i }));
    
    const errorElement = await screen.findByRole('alert');
    expect(errorElement).toHaveTextContent('Search query is required');
  });
  
  it('handles submission errors gracefully', async () => {
    const mockOnSubmit = vi.fn().mockRejectedValue(new Error('Search failed'));
    
    render(<SearchForm onSubmit={mockOnSubmit} />);
    
    await userEvent.type(screen.getByRole('textbox'), 'test query');
    await userEvent.click(screen.getByRole('button', { name: /search/i }));
    
    const errorElement = await screen.findByRole('alert');
    expect(errorElement).toHaveTextContent('Search failed. Please try again.');
  });
  
  it('clears errors on successful submission', async () => {
    const mockOnSubmit = vi.fn()
      .mockRejectedValueOnce(new Error('First attempt failed'))
      .mockResolvedValueOnce(undefined);
    
    render(<SearchForm onSubmit={mockOnSubmit} />);
    
    const searchInput = screen.getByRole('textbox');
    const submitButton = screen.getByRole('button', { name: /search/i });
    
    // First submission fails
    await userEvent.type(searchInput, 'test query');
    await userEvent.click(submitButton);
    
    await screen.findByRole('alert');
    
    // Second submission succeeds
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });
});
```

---

## Business Logic Testing Patterns

### PEP Content Processing Tests

```python
# tests/unit/services/test_content_processor.py
from src.services.content_processor import ContentProcessor

class TestContentProcessor:
    def setup_method(self):
        self.processor = ContentProcessor()
    
    def test_sanitize_pep_content_removes_dangerous_scripts(self):
        """Test content sanitization for security."""
        malicious_content = """
        <h1>PEP Title</h1>
        <script>alert('XSS');</script>
        <p>Valid content</p>
        <iframe src="evil.com"></iframe>
        """
        
        sanitized = self.processor.sanitize_content(malicious_content)
        
        assert "<script>" not in sanitized
        assert "<iframe>" not in sanitized
        assert "<h1>PEP Title</h1>" in sanitized
        assert "<p>Valid content</p>" in sanitized
    
    def test_extract_pep_metadata_from_header(self):
        """Test metadata extraction from PEP headers."""
        pep_content = """
        PEP: 484
        Title: Type Hints
        Author: Guido van Rossum <guido@python.org>
        Status: Final
        Type: Standards Track
        Created: 29-Sep-2014
        Python-Version: 3.5
        """
        
        metadata = self.processor.extract_metadata(pep_content)
        
        assert metadata["number"] == 484
        assert metadata["title"] == "Type Hints"
        assert metadata["status"] == "Final"
        assert metadata["type"] == "Standards Track"
        assert "guido@python.org" in metadata["authors"][0]["email"]
    
    def test_parse_complex_author_field(self):
        """Test parsing of complex author fields."""
        author_line = "Guido van Rossum <guido@python.org>, Barry Warsaw <barry@python.org>"
        
        authors = self.processor.parse_authors(author_line)
        
        assert len(authors) == 2
        assert authors[0]["name"] == "Guido van Rossum"
        assert authors[0]["email"] == "guido@python.org"
        assert authors[1]["name"] == "Barry Warsaw"
        assert authors[1]["email"] == "barry@python.org"
    
    def test_validate_pep_number_format(self):
        """Test PEP number validation and formatting."""
        test_cases = [
            ("1", 1),
            ("0001", 1),
            ("484", 484),
            ("9999", 9999)
        ]
        
        for input_num, expected in test_cases:
            result = self.processor.validate_pep_number(input_num)
            assert result == expected
    
    def test_invalid_pep_number_raises_error(self):
        """Test invalid PEP numbers raise appropriate errors."""
        invalid_numbers = ["0", "-1", "abc", "99999", ""]
        
        for invalid_num in invalid_numbers:
            with pytest.raises(ValueError):
                self.processor.validate_pep_number(invalid_num)
```

### Search Functionality Tests

```python
# tests/unit/services/test_search_service.py
from src.services.search_service import SearchService

class TestSearchService:
    def setup_method(self):
        self.search_service = SearchService()
    
    def test_simple_title_search(self, test_db, sample_peps):
        """Test basic title-based search."""
        results = self.search_service.search_by_title(test_db, "typing")
        
        assert len(results) > 0
        for pep in results:
            assert "typing" in pep.title.lower()
    
    def test_case_insensitive_search(self, test_db, sample_peps):
        """Test search is case insensitive."""
        upper_results = self.search_service.search_by_title(test_db, "TYPE")
        lower_results = self.search_service.search_by_title(test_db, "type")
        
        assert len(upper_results) == len(lower_results)
        assert {p.number for p in upper_results} == {p.number for p in lower_results}
    
    def test_search_with_multiple_terms(self, test_db, sample_peps):
        """Test search with multiple terms."""
        results = self.search_service.search_by_title(test_db, "type hints")
        
        for pep in results:
            title_lower = pep.title.lower()
            assert "type" in title_lower or "hints" in title_lower
    
    def test_search_ranking_by_relevance(self, test_db):
        """Test search results are ranked by relevance."""
        # Create PEPs with different relevance levels
        exact_match = PEPFactory(title="Type Hints")
        partial_match = PEPFactory(title="Advanced Type System")
        weak_match = PEPFactory(title="Python typing module")
        
        test_db.add_all([exact_match, partial_match, weak_match])
        test_db.commit()
        
        results = self.search_service.search_by_title(test_db, "type")
        
        # Results should be ordered by relevance
        assert results[0].title == "Type Hints"  # Exact word match first
    
    def test_empty_search_returns_all_peps(self, test_db, sample_peps):
        """Test empty search query returns all PEPs."""
        results = self.search_service.search_by_title(test_db, "")
        
        total_peps = test_db.query(PEP).count()
        assert len(results) == total_peps
    
    def test_no_results_for_nonexistent_term(self, test_db, sample_peps):
        """Test search for non-existent terms returns empty results."""
        results = self.search_service.search_by_title(test_db, "nonexistentterm123")
        
        assert len(results) == 0
```

### Frontend Business Logic Tests

```typescript
// hooks/usePEPData.test.ts
describe('usePEPData Hook', () => {
  it('loads PEP data on mount', async () => {
    const mockPeps = [
      { number: 1, title: 'PEP 1' },
      { number: 8, title: 'PEP 8' }
    ];
    
    server.use(
      http.get('/api/peps', () => {
        return HttpResponse.json({ peps: mockPeps, total: 2 });
      })
    );
    
    const { result } = renderHook(() => usePEPData());
    
    // Initially loading
    expect(result.current.loading).toBe(true);
    expect(result.current.peps).toEqual([]);
    
    // After loading
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(result.current.peps).toEqual(mockPeps);
    expect(result.current.total).toBe(2);
  });
  
  it('handles pagination correctly', async () => {
    const { result } = renderHook(() => usePEPData());
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    // Test pagination
    act(() => {
      result.current.setPage(2);
    });
    
    expect(result.current.page).toBe(2);
    // Should trigger new API call with updated pagination
  });
  
  it('filters PEPs by status', async () => {
    const { result } = renderHook(() => usePEPData());
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    act(() => {
      result.current.setStatusFilter('Final');
    });
    
    expect(result.current.statusFilter).toBe('Final');
    // Should trigger filtered API call
  });
});

// utils/pepHelpers.test.ts
describe('PEP Helper Functions', () => {
  describe('formatPEPNumber', () => {
    it('formats PEP numbers with leading zeros', () => {
      expect(formatPEPNumber(1)).toBe('PEP 0001');
      expect(formatPEPNumber(42)).toBe('PEP 0042');
      expect(formatPEPNumber(484)).toBe('PEP 0484');
      expect(formatPEPNumber(9999)).toBe('PEP 9999');
    });
  });
  
  describe('getStatusColor', () => {
    it('returns correct colors for each status', () => {
      expect(getStatusColor('Final')).toBe('green');
      expect(getStatusColor('Draft')).toBe('blue');
      expect(getStatusColor('Rejected')).toBe('red');
      expect(getStatusColor('Active')).toBe('purple');
    });
    
    it('returns default color for unknown status', () => {
      expect(getStatusColor('Unknown')).toBe('gray');
    });
  });
  
  describe('parsePEPUrl', () => {
    it('extracts PEP number from URL', () => {
      const url = 'https://peps.python.org/pep-0484/';
      expect(parsePEPUrl(url)).toBe(484);
    });
    
    it('handles various URL formats', () => {
      const testCases = [
        ['https://peps.python.org/pep-0001/', 1],
        ['https://peps.python.org/pep-9999/', 9999],
        ['pep-0042.html', 42]
      ];
      
      testCases.forEach(([url, expected]) => {
        expect(parsePEPUrl(url)).toBe(expected);
      });
    });
  });
});
```

---

## CI/CD Integration Recommendations

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run linting
      working-directory: ./backend
      run: |
        ruff check src tests
        black --check src tests
    
    - name: Run unit tests
      working-directory: ./backend
      run: |
        pytest tests/unit -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      working-directory: ./backend
      run: |
        pytest tests/integration -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Run linting
      working-directory: ./frontend
      run: npm run lint
    
    - name: Run type checking
      working-directory: ./frontend
      run: npm run typecheck
    
    - name: Run unit tests
      working-directory: ./frontend
      run: npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info
        flags: frontend

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install backend dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -e .
    
    - name: Install frontend dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Install E2E dependencies
      working-directory: ./e2e
      run: npm ci
    
    - name: Install Playwright browsers
      working-directory: ./e2e
      run: npx playwright install --with-deps
    
    - name: Build frontend
      working-directory: ./frontend
      run: npm run build
    
    - name: Run E2E tests
      working-directory: ./e2e
      run: npx playwright test
    
    - name: Upload E2E test results
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: playwright-report
        path: e2e/playwright-report/
        retention-days: 30

  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  quality-gate:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests, e2e-tests]
    if: github.event_name == 'pull_request'
    
    steps:
    - name: Quality Gate Check
      run: |
        echo "All tests passed - Quality gate satisfied"
        # Additional quality checks can be added here
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        files: ^backend/
        language_version: python3
  
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.290
    hooks:
      - id: ruff
        files: ^backend/
        args: [--fix, --exit-non-zero-on-fix]
  
  - repo: local
    hooks:
      - id: backend-tests
        name: Backend Unit Tests
        entry: bash -c 'cd backend && python -m pytest tests/unit -x'
        language: system
        files: ^backend/
        pass_filenames: false
      
      - id: frontend-lint
        name: Frontend Lint
        entry: bash -c 'cd frontend && npm run lint'
        language: system
        files: ^frontend/
        pass_filenames: false
      
      - id: frontend-typecheck
        name: Frontend Type Check
        entry: bash -c 'cd frontend && npm run typecheck'
        language: system
        files: ^frontend/
        pass_filenames: false
```

### Coverage Configuration

#### Backend Coverage (.coveragerc)
```ini
[run]
source = src
omit =
    */tests/*
    */venv/*
    */migrations/*
    */__pycache__/*
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod

[html]
directory = htmlcov

[xml]
output = coverage.xml
```

#### Frontend Coverage Configuration
```typescript
// vitest.config.ts - coverage section
coverage: {
  provider: 'v8',
  reporter: ['text', 'html', 'json', 'lcov'],
  exclude: [
    'node_modules/',
    'src/__tests__/',
    '**/*.stories.tsx',
    '**/*.test.{ts,tsx}',
    'src/main.tsx',
    'src/vite-env.d.ts',
    '**/types.ts'
  ],
  thresholds: {
    global: {
      branches: 70,
      functions: 70,
      lines: 80,
      statements: 80
    },
    'src/components/': {
      branches: 80,
      functions: 80,
      lines: 90,
      statements: 90
    },
    'src/services/': {
      branches: 85,
      functions: 85,
      lines: 90,
      statements: 90
    }
  }
}
```

---

## Test Documentation Standards

### Test Case Documentation Template

#### Backend Test Documentation
```python
"""
Test Case: test_pep_repository_search_functionality

Purpose: Verify that the PEP repository correctly implements search functionality
         with proper filtering, ranking, and result formatting.

Preconditions:
- Test database is initialized with sample PEP data
- Sample PEPs include various titles covering different topics
- Database contains at least 10 PEPs for meaningful search results

Test Data:
- PEP 484: "Type Hints" (Final)
- PEP 526: "Variable Annotations" (Final)
- PEP 585: "Type Hinting Generics" (Final)
- PEP 1: "PEP Purpose and Guidelines" (Active)

Test Steps:
1. Initialize PEPRepository with test database session
2. Execute search with query "type"
3. Verify results contain expected PEPs
4. Verify results are properly ranked by relevance
5. Verify no irrelevant PEPs are included

Expected Results:
- Search returns 3 PEPs (484, 526, 585)
- Results are ordered by relevance (exact word matches first)
- Each result contains complete PEP data structure
- No PEPs without "type" in title are returned

Edge Cases Tested:
- Case insensitive search ("Type", "TYPE", "type")
- Empty search query
- Search with no results
- Search with special characters

Dependencies:
- SQLAlchemy session fixture
- Sample PEP data fixtures
- PEPRepository class

Author: [Developer Name]
Created: [Date]
Last Updated: [Date]
"""

def test_pep_repository_search_functionality(test_db, sample_peps):
    # Implementation follows...
```

#### Frontend Test Documentation
```typescript
/**
 * Test Suite: SearchBar Component
 *
 * Purpose: Ensure the SearchBar component provides reliable search functionality
 *          with proper validation, error handling, and user feedback.
 *
 * Component Under Test: SearchBar
 *
 * Key Behaviors Tested:
 * - Renders search input and submit button correctly
 * - Validates user input before submission
 * - Handles submission with loading states
 * - Displays appropriate error messages
 * - Clears form after successful submission
 * - Supports keyboard navigation (Enter key)
 * - Meets accessibility requirements
 *
 * Dependencies:
 * - @testing-library/react for component rendering
 * - @testing-library/user-event for user interactions
 * - MSW for API mocking
 * - Vitest for test framework
 *
 * Mock Requirements:
 * - Search API endpoint (/api/search)
 * - Loading states and error responses
 *
 * Accessibility Requirements:
 * - Proper ARIA labels and roles
 * - Screen reader compatibility
 * - Keyboard navigation support
 * - Focus management
 *
 * Author: [Developer Name]
 * Created: [Date]
 * Last Updated: [Date]
 */

describe('SearchBar Component', () => {
  // Test implementations follow...
});
```

### Test Naming Conventions

#### Backend Test Naming
```python
# Pattern: test_[component]_[action]_[condition]_[expected_outcome]

# Good Examples:
def test_pep_repository_get_by_number_existing_pep_returns_pep():
    pass

def test_pep_repository_get_by_number_nonexistent_pep_returns_none():
    pass

def test_content_processor_sanitize_malicious_html_removes_scripts():
    pass

def test_api_endpoint_get_peps_with_pagination_returns_correct_subset():
    pass

# Bad Examples (avoid these):
def test_pep_stuff():  # Too vague
    pass

def test_repository():  # No action specified
    pass

def test_get_pep_by_number():  # No condition or expected outcome
    pass
```

#### Frontend Test Naming
```typescript
// Pattern: "should [expected behavior] when [condition]"

// Good Examples:
describe('SearchBar', () => {
  it('should display error message when search query is empty', () => {});
  it('should call onSearch callback when form is submitted with valid query', () => {});
  it('should show loading state while search is in progress', () => {});
  it('should clear form after successful search submission', () => {});
});

// Bad Examples (avoid these):
describe('SearchBar', () => {
  it('tests search', () => {});  // Too vague
  it('error handling', () => {});  // No "should" pattern
  it('should work', () => {});  // Not specific enough
});
```

### Documentation Requirements

#### Test Documentation Checklist
- [ ] Purpose and scope clearly defined
- [ ] Preconditions and setup requirements documented
- [ ] Test data and fixtures described
- [ ] Expected outcomes specified
- [ ] Edge cases and error scenarios covered
- [ ] Dependencies and mocks identified
- [ ] Author and maintenance information included
- [ ] Accessibility requirements noted (for frontend)
- [ ] Performance expectations documented (if applicable)

#### Test Maintenance Guidelines
1. **Update Documentation**: When modifying tests, update documentation
2. **Review Test Names**: Ensure test names remain descriptive and accurate
3. **Deprecation Notices**: Mark outdated tests for removal
4. **Test Categories**: Use appropriate markers/tags for test organization
5. **Performance Tracking**: Document test execution time expectations

---

## Performance and Security Testing Considerations

### Performance Testing Strategy

#### Backend Performance Tests

```python
# tests/performance/test_api_performance.py
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, stdev

class TestAPIPerformance:
    
    @pytest.mark.performance
    async def test_get_peps_response_time(self, client, large_dataset):
        """Test API response time under normal load."""
        start_time = time.time()
        
        response = await client.get("/api/peps?limit=100")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.5  # 500ms threshold
    
    @pytest.mark.performance
    async def test_search_performance_with_large_dataset(self, client, large_dataset):
        """Test search performance with substantial data."""
        search_queries = ["type", "async", "import", "class", "function"]
        response_times = []
        
        for query in search_queries:
            start_time = time.time()
            response = await client.get(f"/api/search?q={query}")
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            assert response.status_code == 200
        
        avg_response_time = mean(response_times)
        assert avg_response_time < 1.0  # 1 second average threshold
        assert max(response_times) < 2.0  # 2 seconds max threshold
    
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_concurrent_requests_performance(self, client):
        """Test API performance under concurrent load."""
        async def make_request():
            response = await client.get("/api/peps?limit=10")
            return response.status_code, time.time()
        
        # Simulate 20 concurrent requests
        start_time = time.time()
        tasks = []
        
        for _ in range(20):
            task = asyncio.create_task(make_request())
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All requests should succeed
        assert all(status == 200 for status, _ in results)
        
        # Total time should be reasonable (requests should be handled concurrently)
        total_time = end_time - start_time
        assert total_time < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.performance
    def test_database_query_performance(self, test_db, large_pep_dataset):
        """Test database query performance."""
        repo = PEPRepository(test_db)
        
        # Test simple query performance
        start_time = time.time()
        pep = repo.get_pep_by_number(1)
        query_time = time.time() - start_time
        
        assert pep is not None
        assert query_time < 0.1  # 100ms threshold for simple queries
        
        # Test search query performance
        start_time = time.time()
        results = repo.search_peps_by_title("python")
        search_time = time.time() - start_time
        
        assert len(results) > 0
        assert search_time < 0.5  # 500ms threshold for search queries
```

#### Frontend Performance Tests

```typescript
// tests/performance/component-performance.test.tsx
describe('Component Performance', () => {
  it('should render PEP list quickly with large dataset', async () => {
    const largePEPList = Array.from({ length: 1000 }, (_, i) => ({
      number: i + 1,
      title: `PEP ${i + 1}`,
      status: 'Final',
      type: 'Standards Track',
      topic: 'Core',
      created: '2023-01-01',
      python_version: null,
      url: `https://peps.python.org/pep-${String(i + 1).padStart(4, '0')}/`,
      authors: [{ id: 1, name: 'Test Author' }]
    }));

    server.use(
      http.get('/api/peps', () => {
        return HttpResponse.json({
          peps: largePEPList,
          total: largePEPList.length
        });
      })
    );

    const startTime = performance.now();
    
    render(<PEPList />);
    
    await waitFor(() => {
      expect(screen.getByText('PEP 1')).toBeInTheDocument();
    });
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should render within reasonable time
    expect(renderTime).toBeLessThan(1000); // 1 second
  });

  it('should handle search input changes efficiently', async () => {
    render(<SearchBar onSearch={vi.fn()} />);
    
    const searchInput = screen.getByRole('textbox');
    const longSearchTerm = 'a'.repeat(100);
    
    const startTime = performance.now();
    
    await userEvent.type(searchInput, longSearchTerm);
    
    const endTime = performance.now();
    const inputTime = endTime - startTime;
    
    // Typing should be responsive
    expect(inputTime).toBeLessThan(500); // 500ms
    expect(searchInput).toHaveValue(longSearchTerm);
  });
});

// tests/performance/bundle-size.test.ts
describe('Bundle Size Performance', () => {
  it('should maintain reasonable bundle size', () => {
    // This would be implemented with build tools
    // to check bundle size and fail if it exceeds thresholds
    const maxBundleSize = 500 * 1024; // 500KB
    // Implementation would check actual bundle size
    expect(true).toBe(true); // Placeholder
  });
});
```

### Security Testing Framework

#### Backend Security Tests

```python
# tests/security/test_input_validation.py
import pytest
from sqlalchemy.exc import IntegrityError

class TestInputValidation:
    
    @pytest.mark.security
    async def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attacks."""
        malicious_inputs = [
            "'; DROP TABLE peps; --",
            "1' OR '1'='1",
            "1; DELETE FROM peps WHERE 1=1; --",
            "UNION SELECT * FROM peps--"
        ]
        
        for malicious_input in malicious_inputs:
            response = await client.get(f"/api/search?q={malicious_input}")
            
            # Should not cause server error or expose data
            assert response.status_code in [200, 400, 422]
            
            # Verify database integrity (all PEPs still exist)
            pep_count_response = await client.get("/api/peps")
            assert pep_count_response.status_code == 200
    
    @pytest.mark.security
    async def test_xss_protection_in_responses(self, client):
        """Test protection against XSS in API responses."""
        # This assumes we have a way to inject test data
        xss_payload = "<script>alert('xss')</script>"
        
        response = await client.get(f"/api/search?q={xss_payload}")
        
        assert response.status_code == 200
        response_text = response.text
        
        # Ensure script tags are not present in response
        assert "<script>" not in response_text
        assert "javascript:" not in response_text.lower()
    
    @pytest.mark.security
    async def test_path_traversal_protection(self, client):
        """Test protection against path traversal attacks."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2f",
            "....//....//....//etc/passwd"
        ]
        
        for malicious_path in malicious_paths:
            response = await client.get(f"/api/peps/{malicious_path}")
            
            # Should return 404 or 400, not expose files
            assert response.status_code in [404, 400, 422]
            
            # Response should not contain file contents
            assert "root:" not in response.text  # Common in /etc/passwd
    
    @pytest.mark.security
    async def test_rate_limiting(self, client):
        """Test API rate limiting functionality."""
        # Make rapid requests
        responses = []
        for _ in range(100):
            response = await client.get("/api/peps")
            responses.append(response)
        
        # Should eventually hit rate limit
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes  # Too Many Requests
    
    @pytest.mark.security
    async def test_cors_headers(self, client):
        """Test CORS headers are properly configured."""
        response = await client.options("/api/peps")
        
        # Check for proper CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        
        # Ensure not wildcard in production
        origin = response.headers.get("Access-Control-Allow-Origin")
        if os.getenv("ENVIRONMENT") == "production":
            assert origin != "*"

# tests/security/test_authentication_security.py (future)
class TestAuthenticationSecurity:
    
    @pytest.mark.security
    async def test_jwt_token_validation(self, client):
        """Test JWT token validation and security."""
        # Test with malformed token
        malformed_token = "invalid.jwt.token"
        headers = {"Authorization": f"Bearer {malformed_token}"}
        
        response = await client.get("/api/admin/peps", headers=headers)
        assert response.status_code == 401
    
    @pytest.mark.security
    async def test_password_hashing(self, test_db):
        """Test password hashing security."""
        from src.models.auth import User
        
        plaintext_password = "testpassword123"
        user = User(username="testuser", password=plaintext_password)
        
        # Password should be hashed, not stored in plaintext
        assert user.password_hash != plaintext_password
        assert len(user.password_hash) > 50  # Reasonable hash length
        assert "$" in user.password_hash  # bcrypt format indicator
    
    @pytest.mark.security
    async def test_session_management(self, client, auth_headers):
        """Test secure session management."""
        # Test session timeout
        # Test session invalidation on logout
        # Test concurrent session limits
        pass
```

#### Frontend Security Tests

```typescript
// tests/security/xss-protection.test.tsx
describe('XSS Protection', () => {
  it('should sanitize user input in search results', async () => {
    const xssPayload = '<script>alert("xss")</script>';
    const mockPEP = {
      number: 999,
      title: `Malicious PEP ${xssPayload}`,
      status: 'Draft',
      type: 'Standards Track',
      topic: 'Security',
      created: '2023-01-01',
      python_version: null,
      url: 'https://peps.python.org/pep-0999/',
      authors: [{ id: 1, name: 'Test Author' }]
    };

    server.use(
      http.get('/api/search', () => {
        return HttpResponse.json({
          peps: [mockPEP],
          total: 1
        });
      })
    );

    render(<SearchResultPage searchTerm="malicious" />);

    await waitFor(() => {
      const titleElement = screen.getByText(/Malicious PEP/);
      expect(titleElement).toBeInTheDocument();
    });

    // Verify script tag is not executed
    const titleElement = screen.getByText(/Malicious PEP/);
    expect(titleElement.innerHTML).not.toContain('<script>');
  });

  it('should handle malicious URLs safely', () => {
    const maliciousURL = 'javascript:alert("xss")';
    
    render(<PEPListItem pep={{
      number: 1,
      title: 'Test PEP',
      status: 'Final',
      type: 'Standards Track',
      topic: 'Core',
      created: '2023-01-01',
      python_version: null,
      url: maliciousURL,
      authors: []
    }} />);

    const linkElement = screen.getByRole('link');
    
    // Should not allow javascript: URLs
    expect(linkElement.getAttribute('href')).not.toBe(maliciousURL);
    expect(linkElement.getAttribute('href')).toMatch(/^https?:\/\//);
  });
});

// tests/security/content-security.test.tsx
describe('Content Security', () => {
  it('should validate external links', () => {
    const suspiciousLinks = [
      'http://malicious-site.com',
      'ftp://suspicious-server.net',
      'javascript:void(0)'
    ];

    suspiciousLinks.forEach(link => {
      const { result } = renderHook(() => useSecureLink(link));
      
      // Should either sanitize or reject suspicious links
      expect(result.current.isSafe).toBe(false);
      expect(result.current.sanitizedUrl).not.toBe(link);
    });
  });

  it('should implement CSP compliance', () => {
    // Test that components don't violate Content Security Policy
    render(<App />);
    
    // Check for inline styles (should be avoided)
    const elementsWithInlineStyle = document.querySelectorAll('[style]');
    expect(elementsWithInlineStyle.length).toBe(0);
    
    // Check for inline event handlers (should be avoided)
    const elementsWithOnClick = document.querySelectorAll('[onclick]');
    expect(elementsWithOnClick.length).toBe(0);
  });
});
```

### Performance Monitoring Setup

```typescript
// utils/performance-monitor.ts
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, number[]> = new Map();

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  recordMetric(name: string, value: number): void {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(value);
  }

  getAverageMetric(name: string): number {
    const values = this.metrics.get(name) || [];
    return values.length > 0 ? values.reduce((a, b) => a + b) / values.length : 0;
  }

  clearMetrics(): void {
    this.metrics.clear();
  }
}

// Usage in tests
export const measureComponentRender = (component: ReactElement): number => {
  const start = performance.now();
  render(component);
  const end = performance.now();
  return end - start;
};
```

---

## Implementation Roadmap

### Phase 1: Foundation Setup (Week 1-2)

#### Backend Foundation
- [ ] Enhanced [`conftest.py`](backend/tests/conftest.py) with comprehensive fixtures
- [ ] [`pytest.ini`](backend/pytest.ini) configuration
- [ ] Test database setup and teardown utilities
- [ ] Basic test factories using [`factory-boy`](backend/tests/utils/factories.py)
- [ ] Custom assertion helpers in [`backend/tests/utils/assertions.py`](backend/tests/utils/assertions.py)

#### Frontend Foundation
- [ ] [`vitest.config.ts`](frontend/vitest.config.ts) configuration
- [ ] MSW setup for API mocking in [`frontend/src/__tests__/utils/mock-api.ts`](frontend/src/__tests__/utils/mock-api.ts)
- [ ] Custom render utilities in [`frontend/src/__tests__/utils/test-utils.tsx`](frontend/src/__tests__/utils/test-utils.tsx)
- [ ] Test fixtures and data in [`frontend/src/__tests__/utils/fixtures.ts`](frontend/src/__tests__/utils/fixtures.ts)

#### CI/CD Setup
- [ ] GitHub Actions workflow configuration
- [ ] Pre-commit hooks setup
- [ ] Coverage reporting integration
- [ ] Quality gates and checks

**Deliverables:**
- Complete test infrastructure setup
- Basic test examples for each layer
- Documentation for test setup and execution
- CI/CD pipeline with basic quality checks

### Phase 2: Core Unit Testing (Week 3-4)

#### Backend Unit Tests
- [ ] Model tests for [`PEP`](backend/src/models/orm_models.py:31) and [`Author`](backend/src/models/orm_models.py:64) classes
- [ ] Repository layer tests for [`PEPRepository`](backend/src/services/pep_repository.py:7)
- [ ] Service layer tests for content processing
- [ ] Validation and error handling tests
- [ ] Database operation tests

#### Frontend Unit Tests
- [ ] Component tests for all UI components
- [ ] Service layer tests for [`api.ts`](frontend/src/services/api.ts)
- [ ] Utility function tests
- [ ] Hook tests for custom React hooks
- [ ] Form validation tests

**Deliverables:**
- 80%+ unit test coverage for both backend and frontend
- Comprehensive test suites for core functionality
- Test documentation and examples
- Automated test execution in CI/CD

### Phase 3: Integration Testing (Week 5-6)

#### API Integration Tests
- [ ] Endpoint tests for [`/api/peps`](backend/src/app.py:20), [`/api/peps/{number}`](backend/src/app.py:33), [`/api/search`](backend/src/app.py:43)
- [ ] Database integration tests
- [ ] Request/response validation tests
- [ ] Error handling and edge case tests
- [ ] Performance baseline tests

#### Frontend Integration Tests
- [ ] Component integration with API services
- [ ] Route and navigation tests
- [ ] Form submission and validation integration
- [ ] State management integration tests
- [ ] Error boundary and error handling tests

**Deliverables:**
- Complete API test coverage
- Integration test suite execution
- Performance baseline establishment
- Error handling verification

### Phase 4: End-to-End Testing (Week 7-8)

#### E2E Test Implementation
- [ ] Playwright configuration and setup
- [ ] User journey tests (browse, search, view details)
- [ ] Cross-browser compatibility tests
- [ ] Mobile responsiveness tests
- [ ] Accessibility testing integration

#### Test Environment Setup
- [ ] Test data management and seeding
- [ ] Environment configuration
- [ ] Test execution optimization
- [ ] Reporting and monitoring setup

**Deliverables:**
- Complete E2E test suite
- Cross-browser testing capability
- Automated accessibility testing
- Comprehensive test reporting

### Phase 5: Advanced Testing Features (Week 9-10)

#### Authentication Testing (Future-Ready)
- [ ] Authentication flow test framework
- [ ] JWT token validation tests
- [ ] Permission and authorization tests
- [ ] Security testing suite

#### Performance & Security Testing
- [ ] Load testing implementation
- [ ] Security vulnerability scanning
- [ ] Performance monitoring setup
- [ ] Stress testing scenarios

#### Advanced Features
- [ ] Visual regression testing setup
- [ ] Database migration testing
- [ ] API versioning test support
- [ ] Monitoring and alerting integration

**Deliverables:**
- Future-ready authentication testing framework
- Performance and security testing suites
- Advanced testing capabilities
- Comprehensive monitoring setup

### Phase 6: Documentation and Training (Week 11-12)

#### Documentation Completion
- [ ] Complete test documentation
- [ ] Development workflow documentation
- [ ] Troubleshooting guides
- [ ] Best practices documentation

#### Team Training and Adoption
- [ ] TDD methodology training
- [ ] Test writing guidelines
- [ ] Code review processes
- [ ] Quality assurance procedures

**Deliverables:**
- Complete testing documentation
- Team training materials
- Established development processes
- Quality assurance framework

---

## Success Metrics and Quality Gates

### Coverage Targets

#### Backend Coverage Goals
- **Unit Tests**: 85% line coverage, 80% branch coverage
- **Integration Tests**: 90% API endpoint coverage
- **Critical Paths**: 95% coverage for core business logic

#### Frontend Coverage Goals
- **Components**: 80% line coverage, 75% branch coverage
- **Services**: 90% line coverage, 85% branch coverage
- **User Interactions**: 85% coverage for critical user flows

### Quality Gates

#### Pre-Merge Requirements
- [ ] All tests passing (unit, integration, E2E)
- [ ] Coverage thresholds met
- [ ] No security vulnerabilities detected
- [ ] Performance benchmarks met
- [ ] Code quality checks passed (linting, formatting)

#### Release Requirements
- [ ] Full test suite execution (all browsers)
- [ ] Performance testing completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Accessibility compliance verified

### Monitoring and Alerts

#### Test Execution Monitoring
- Test execution time trends
- Flaky test identification and resolution
- Coverage trend monitoring
- Performance regression detection

#### Quality Metrics Dashboard
- Test success rates
- Coverage percentages
- Performance metrics
- Security scan results
- Code quality scores

---

## Conclusion

This comprehensive TDD architecture design provides PEPBoy with a robust, scalable testing framework that addresses all current requirements while preparing for future enhancements. The phased implementation approach ensures systematic delivery of testing capabilities, with each phase building upon the previous to create a complete quality assurance ecosystem.

The design emphasizes:

- **Comprehensive Coverage**: Unit, integration, and E2E testing across both backend and frontend
- **Modern Tooling**: Industry-standard frameworks optimized for each technology stack
- **Future Readiness**: Authentication and advanced feature testing preparation
- **Quality Assurance**: Automated quality gates and continuous monitoring
- **Developer Experience**: Clear documentation, helpful utilities, and efficient workflows
- **Maintainability**: Structured test organization and clear maintenance procedures

By following this architecture design, the PEPBoy development team will establish a solid foundation for Test-Driven Development that supports both current development needs and future growth requirements.

The implementation roadmap provides a clear path forward, with measurable milestones and deliverables that ensure successful adoption of comprehensive testing practices. Regular review and refinement of the testing strategy will ensure it continues to serve the project's evolving needs effectively.

This testing architecture will enable the team to:
- **Build with Confidence**: Comprehensive test coverage ensures reliable functionality
- **Iterate Rapidly**: Fast feedback loops enable quick development cycles
- **Scale Effectively**: Well-structured testing infrastructure supports project growth
- **Maintain Quality**: Automated quality gates prevent regression and maintain standards
- **Deploy Safely**: Thorough testing provides confidence in production releases

The successful implementation of this TDD strategy will position PEPBoy as a robust, maintainable, and scalable application that can confidently serve the Python community's needs for accessing and managing Python Enhancement Proposals.
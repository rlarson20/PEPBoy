# Frontend Testing Documentation

This directory contains comprehensive test utilities and documentation for the PEPBoy frontend application, implementing Test-Driven Development (TDD) methodology with React Testing Library and Vitest.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Test Configuration](#test-configuration)
- [Running Tests](#running-tests)
- [TDD Methodology](#tdd-methodology)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Test Utilities](#test-utilities)
- [Component Testing](#component-testing)
- [Service Testing](#service-testing)
- [Accessibility Testing](#accessibility-testing)
- [Performance Testing](#performance-testing)

## Directory Structure

```
frontend/src/
├── test-utils/              # Test utilities and setup
│   ├── README.md           # This file
│   ├── setup-tests.ts      # Global test setup and MSW configuration
│   └── test-utils.tsx      # Custom render functions and utilities
├── components/__tests__/    # Component tests
│   ├── SearchBar.test.tsx  # SearchBar component tests
│   └── PEPList.test.tsx    # PEPList component tests
└── services/__tests__/      # Service layer tests
    └── api.test.ts         # API service tests
```

## Test Configuration

### vitest.config.ts

The project uses Vitest with the following key configurations:

- **Environment**: jsdom for DOM testing
- **Global Imports**: React Testing Library and Vitest globals
- **Coverage**: 85% minimum coverage requirement
- **Setup Files**: Automatic test environment setup

### Dependencies

Key testing dependencies (defined in `package.json`):

```json
{
  "devDependencies": {
    "vitest": "^2.1.5",
    "@testing-library/react": "^16.1.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/user-event": "^14.5.2",
    "jsdom": "^25.0.1",
    "msw": "^2.6.8",
    "@types/node": "^22.10.2"
  }
}
```

## Running Tests

### Basic Commands

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test SearchBar.test.tsx

# Run tests matching pattern
npm test -- --grep "SearchBar"
```

### Test Scripts

Available npm scripts:

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:watch": "vitest --watch"
  }
}
```

## TDD Methodology

This project follows the **Red-Green-Refactor** cycle for React components:

### 1. Red Phase
Write a failing test that defines the expected component behavior:

```tsx
describe('SearchBar Component', () => {
  it('should render search input field', () => {
    // TDD Red: This test will fail until SearchBar is implemented
    renderWithProviders(<SearchBar />)
    
    const searchInput = screen.getByLabelText(/search peps/i)
    expect(searchInput).toBeInTheDocument()
    expect(searchInput).toHaveAttribute('type', 'text')
  })
})
```

### 2. Green Phase
Implement minimal component to make the test pass:

```tsx
function SearchBar() {
  return (
    <div>
      <label htmlFor="search">Search PEPs</label>
      <input id="search" type="text" />
    </div>
  )
}
```

### 3. Refactor Phase
Enhance the component while keeping tests green:

```tsx
function SearchBar({ onSearch, isLoading, error }) {
  const [query, setQuery] = useState('')
  
  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="search">Search PEPs</label>
      <input 
        id="search" 
        type="text" 
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        disabled={isLoading}
      />
      <button type="submit" disabled={isLoading}>
        Search
      </button>
      {error && <div role="alert">{error}</div>}
    </form>
  )
}
```

## Test Categories

### Component Tests (`components/__tests__/`)

Test React components in isolation:

- **Rendering**: Component displays correctly
- **User Interactions**: Click, type, keyboard navigation
- **Props**: Different prop combinations
- **State Changes**: Component state updates
- **Error Handling**: Error states and boundaries

### Service Tests (`services/__tests__/`)

Test business logic and API interactions:

- **API Calls**: HTTP requests and responses
- **Error Handling**: Network failures, server errors
- **Data Transformation**: Request/response processing
- **Caching**: Request caching behavior

### Integration Tests

Test component interactions and workflows:

- **User Workflows**: Complete user journeys
- **Component Communication**: Parent-child interactions
- **Routing**: Navigation and URL handling

## Writing Tests

### Test Structure Guidelines

Follow the **Arrange-Act-Assert** pattern:

```tsx
describe('Component', () => {
  const user = userEvent.setup()
  
  it('should do something when condition', async () => {
    // Arrange: Set up component and test data
    const mockOnClick = vi.fn()
    renderWithProviders(<Component onClick={mockOnClick} />)
    
    // Act: Perform user interaction
    const button = screen.getByRole('button')
    await user.click(button)
    
    // Assert: Verify expected behavior
    expect(mockOnClick).toHaveBeenCalledWith(expectedData)
  })
})
```

### Naming Conventions

- Test files: `*.test.tsx` or `*.test.ts`
- Test suites: `describe('ComponentName', () => {})`
- Test cases: `it('should do what when condition', () => {})`

**Examples:**
```tsx
describe('SearchBar Component', () => {
  describe('Component Rendering', () => {
    it('should render search input field', () => {})
    it('should render search button', () => {})
  })
  
  describe('User Interactions', () => {
    it('should call onSearch when form is submitted', () => {})
    it('should not submit empty search', () => {})
  })
})
```

## Test Utilities

### Custom Render Function

Use `renderWithProviders` for components that need context:

```tsx
import { renderWithProviders } from '../test-utils/test-utils'

// Renders component with Router and other providers
const { getByText, rerender } = renderWithProviders(
  <ComponentNeedingRouter />,
  { route: '/custom-route' }
)
```

### Mock Data Creation

Use utility functions for consistent test data:

```tsx
import { createMockPep, testData } from '../test-utils/test-utils'

// Create single mock PEP
const mockPep = createMockPep({ number: 123, title: 'Custom Title' })

// Create multiple PEPs
const mockPeps = testData.pepList(5)

// Create search results
const searchResults = testData.searchResults('python', 3)
```

### API Mocking

Tests use MSW (Mock Service Worker) for API mocking:

```tsx
import { server } from '../test-utils/setup-tests'
import { rest } from 'msw'

// Override default handler for specific test
server.use(
  rest.get('/api/peps', (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({ error: 'Server error' }))
  })
)
```

### User Event Testing

Use `@testing-library/user-event` for realistic interactions:

```tsx
import userEvent from '@testing-library/user-event'

const user = userEvent.setup()

// Type in input
await user.type(searchInput, 'test query')

// Click button
await user.click(submitButton)

// Keyboard navigation
await user.keyboard('{Tab}{Enter}')

// Complex interactions
await user.clear(searchInput)
await user.type(searchInput, 'new query')
await user.keyboard('{Enter}')
```

## Component Testing

### Testing Patterns

#### Rendering Tests
```tsx
it('should render with correct initial state', () => {
  renderWithProviders(<Component />)
  
  expect(screen.getByRole('textbox')).toBeInTheDocument()
  expect(screen.getByRole('button')).toBeEnabled()
})
```

#### Props Testing
```tsx
it('should display error message when error prop provided', () => {
  const errorMessage = 'Something went wrong'
  renderWithProviders(<Component error={errorMessage} />)
  
  expect(screen.getByRole('alert')).toHaveTextContent(errorMessage)
})
```

#### Event Handling
```tsx
it('should call onChange when input value changes', async () => {
  const mockOnChange = vi.fn()
  renderWithProviders(<Component onChange={mockOnChange} />)
  
  const input = screen.getByRole('textbox')
  await user.type(input, 'test')
  
  expect(mockOnChange).toHaveBeenCalledWith('test')
})
```

#### State Testing
```tsx
it('should update display when internal state changes', async () => {
  renderWithProviders(<Component />)
  
  const button = screen.getByRole('button', { name: /toggle/i })
  await user.click(button)
  
  expect(screen.getByText(/active/i)).toBeInTheDocument()
})
```

### Loading States

```tsx
it('should show loading spinner when isLoading is true', () => {
  renderWithProviders(<Component isLoading={true} />)
  
  expect(screen.getByRole('status')).toBeInTheDocument()
  expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
})
```

### Error Boundaries

```tsx
it('should catch and display errors gracefully', () => {
  const ThrowError = () => {
    throw new Error('Test error')
  }
  
  renderWithProviders(
    <ErrorBoundary>
      <ThrowError />
    </ErrorBoundary>
  )
  
  expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
})
```

## Service Testing

### API Service Testing

```tsx
describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should fetch PEPs successfully', async () => {
    const mockResponse = { peps: [], total: 0 }
    mockedAxios.get.mockResolvedValueOnce({ data: mockResponse })

    const result = await fetchPeps()

    expect(mockedAxios.get).toHaveBeenCalledWith('/peps', {
      params: { page: 1, per_page: 10 }
    })
    expect(result).toEqual(mockResponse)
  })

  it('should handle API errors', async () => {
    const error = { response: { status: 500, data: { message: 'Server error' } } }
    mockedAxios.get.mockRejectedValueOnce(error)

    await expect(fetchPeps()).rejects.toThrow('API Error: 500 - Server error')
  })
})
```

### Async Testing

```tsx
it('should handle async operations correctly', async () => {
  const promise = asyncFunction()
  
  // Test loading state
  expect(screen.getByRole('status')).toBeInTheDocument()
  
  // Wait for completion
  await promise
  
  // Test final state
  expect(screen.getByText(/completed/i)).toBeInTheDocument()
})
```

## Accessibility Testing

### Basic A11y Tests

```tsx
it('should be accessible', () => {
  renderWithProviders(<Component />)
  
  // Check for proper labels
  expect(screen.getByLabelText(/search/i)).toBeInTheDocument()
  
  // Check for ARIA attributes
  const button = screen.getByRole('button')
  expect(button).toHaveAccessibleName()
  
  // Check for keyboard navigation
  expect(button).toHaveAttribute('tabindex', '0')
})
```

### Screen Reader Testing

```tsx
it('should announce state changes to screen readers', async () => {
  renderWithProviders(<Component />)
  
  const status = screen.getByRole('status')
  expect(status).toHaveAttribute('aria-live', 'polite')
  
  // Trigger state change
  await user.click(screen.getByRole('button'))
  
  expect(status).toHaveTextContent(/loading/i)
})
```

### Focus Management

```tsx
it('should manage focus correctly', async () => {
  renderWithProviders(<Component />)
  
  const input = screen.getByRole('textbox')
  const button = screen.getByRole('button')
  
  // Tab through elements
  await user.tab()
  expect(input).toHaveFocus()
  
  await user.tab()
  expect(button).toHaveFocus()
})
```

## Performance Testing

### Render Performance

```tsx
it('should render within acceptable time', async () => {
  const startTime = performance.now()
  
  renderWithProviders(<Component />)
  
  const endTime = performance.now()
  const renderTime = endTime - startTime
  
  expect(renderTime).toBeLessThan(100) // 100ms threshold
})
```

### Memory Leaks

```tsx
it('should not cause memory leaks', () => {
  const { unmount } = renderWithProviders(<Component />)
  
  // Check initial memory usage
  const initialMemory = performance.memory?.usedJSHeapSize
  
  // Unmount component
  unmount()
  
  // Force garbage collection (if available)
  if (global.gc) {
    global.gc()
  }
  
  // Memory should not significantly increase
  const finalMemory = performance.memory?.usedJSHeapSize
  expect(finalMemory).toBeLessThanOrEqual(initialMemory * 1.1)
})
```

## Best Practices

### Test Organization

```tsx
describe('ComponentName', () => {
  // Setup
  const user = userEvent.setup()
  
  beforeEach(() => {
    vi.clearAllMocks()
  })
  
  // Group related tests
  describe('Rendering', () => {
    // Rendering tests
  })
  
  describe('User Interactions', () => {
    // Interaction tests
  })
  
  describe('Error Handling', () => {
    // Error tests
  })
})
```

### Mock Management

```tsx
// Mock at module level
vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn(),
  useLocation: vi.fn(() => ({ pathname: '/' }))
}))

// Reset mocks between tests
beforeEach(() => {
  vi.clearAllMocks()
})
```

### Async Testing

```tsx
// Wait for elements to appear
await waitFor(() => {
  expect(screen.getByText(/loaded/i)).toBeInTheDocument()
})

// Wait for elements to disappear
await waitForElementToBeRemoved(screen.getByTestId('loading'))

// Find elements asynchronously
const element = await screen.findByText(/async content/i)
```

### Error Testing

```tsx
// Test error boundaries
it('should handle component errors', () => {
  const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
  
  renderWithProviders(<ComponentThatThrows />)
  
  expect(screen.getByText(/error occurred/i)).toBeInTheDocument()
  
  spy.mockRestore()
})
```

## Debugging Tests

### Debug Utilities

```tsx
import { screen } from '@testing-library/react'

// Debug rendered DOM
screen.debug()

// Debug specific element
screen.debug(screen.getByRole('button'))

// Log queries
screen.logTestingPlaygroundURL()
```

### Common Issues

1. **Element not found**: Use `findBy*` for async elements
2. **Act warnings**: Wrap state updates in `act()`
3. **Timer issues**: Mock timers with `vi.useFakeTimers()`
4. **Memory leaks**: Properly unmount components and clear mocks

## Coverage Requirements

- **Line Coverage**: 85% minimum
- **Branch Coverage**: 85% minimum  
- **Function Coverage**: 85% minimum
- **Statement Coverage**: 85% minimum

### Coverage Reports

```bash
# Generate coverage report
npm run test:coverage

# View HTML report
open coverage/index.html
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest DOM Matchers](https://github.com/testing-library/jest-dom)
- [User Event](https://testing-library.com/docs/user-event/intro/)
- [MSW Documentation](https://mswjs.io/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
/**
 * Custom test utilities for React Testing Library.
 * 
 * This module provides custom render functions and utilities that wrap
 * React Testing Library with common providers and setup.
 */

import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { vi } from 'vitest'

// Define types for our test utilities
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string
  initialEntries?: string[]
}

interface MockApiResponse {
  peps?: Array<{
    number: number
    title: string
    status: string
    type: string
    topic: string
    created: string
    url: string
    authors: string[]
  }>
  total?: number
  skip?: number
  limit?: number
}

/**
 * Custom render function that includes common providers.
 * 
 * @param ui - The React component to render
 * @param options - Render options including custom route
 * @returns Render result with additional utilities
 */
export function renderWithProviders(
  ui: ReactElement,
  options: CustomRenderOptions = {}
) {
  const { route = '/', initialEntries = [route], ...renderOptions } = options

  // Create a wrapper component with providers
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <BrowserRouter>
        {children}
      </BrowserRouter>
    )
  }

  // Render the component with providers
  const result = render(ui, {
    wrapper: Wrapper,
    ...renderOptions,
  })

  return {
    ...result,
    // Add custom utilities
    rerender: (newUi: ReactElement) =>
      renderWithProviders(newUi, { container: result.container, route }),
  }
}

/**
 * Custom render function for testing components in isolation without providers.
 * 
 * @param ui - The React component to render
 * @param options - Standard render options
 * @returns Standard render result
 */
export function renderWithoutProviders(
  ui: ReactElement,
  options: RenderOptions = {}
) {
  return render(ui, options)
}

/**
 * Create mock API responses for testing.
 */
export const createMockApiResponse = (
  overrides: Partial<MockApiResponse> = {}
): MockApiResponse => ({
  peps: [
    {
      number: 1,
      title: 'PEP Purpose and Guidelines',
      status: 'Active',
      type: 'Process',
      topic: 'Core',
      created: '2000-06-13',
      url: 'https://peps.python.org/pep-0001/',
      authors: ['Barry Warsaw', 'Jeremy Hylton']
    },
    {
      number: 8,
      title: 'Style Guide for Python Code',
      status: 'Active',
      type: 'Process',
      topic: 'Core',
      created: '2001-07-05',
      url: 'https://peps.python.org/pep-0008/',
      authors: ['Guido van Rossum', 'Barry Warsaw']
    }
  ],
  total: 2,
  skip: 0,
  limit: 10,
  ...overrides,
})

/**
 * Create a mock PEP object for testing.
 */
export const createMockPep = (overrides: Record<string, any> = {}) => ({
  number: 1,
  title: 'Test PEP',
  status: 'Draft',
  type: 'Standards Track',
  topic: 'Core',
  created: '2024-01-01',
  url: 'https://peps.python.org/pep-0001/',
  authors: ['Test Author'],
  ...overrides,
})

/**
 * Mock the fetch API for testing.
 */
export const mockFetch = (
  response: any,
  options: { status?: number; ok?: boolean } = {}
) => {
  const { status = 200, ok = true } = options
  
  return vi.fn().mockResolvedValue({
    ok,
    status,
    json: vi.fn().mockResolvedValue(response),
    text: vi.fn().mockResolvedValue(JSON.stringify(response)),
  })
}

/**
 * Mock axios responses for testing.
 */
export const mockAxiosResponse = (data: any, status = 200) => ({
  data,
  status,
  statusText: 'OK',
  headers: {},
  config: {},
})

/**
 * Create a mock intersection observer for testing.
 */
export const createMockIntersectionObserver = () => {
  const mockIntersectionObserver = vi.fn()
  mockIntersectionObserver.mockReturnValue({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  })
  
  Object.defineProperty(window, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: mockIntersectionObserver,
  })
  
  return mockIntersectionObserver
}

/**
 * Wait for a specific amount of time in tests.
 */
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * Mock local storage for testing.
 */
export const mockLocalStorage = () => {
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }
  
  Object.defineProperty(window, 'localStorage', {
    writable: true,
    value: localStorageMock,
  })
  
  return localStorageMock
}

/**
 * Mock session storage for testing.
 */
export const mockSessionStorage = () => {
  const sessionStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }
  
  Object.defineProperty(window, 'sessionStorage', {
    writable: true,
    value: sessionStorageMock,
  })
  
  return sessionStorageMock
}

/**
 * Create mock router hooks for testing.
 */
export const createMockRouterHooks = () => ({
  useNavigate: vi.fn(),
  useLocation: vi.fn(() => ({ pathname: '/', search: '', hash: '', state: null })),
  useParams: vi.fn(() => ({})),
  useSearchParams: vi.fn(() => [new URLSearchParams(), vi.fn()]),
})

/**
 * Test data generators for consistent test data.
 */
export const testData = {
  pep: createMockPep,
  apiResponse: createMockApiResponse,
  
  pepList: (count = 5) => 
    Array.from({ length: count }, (_, i) => 
      createMockPep({ 
        number: i + 1, 
        title: `Test PEP ${i + 1}` 
      })
    ),
  
  searchResults: (query = 'test', count = 3) => ({
    peps: Array.from({ length: count }, (_, i) => 
      createMockPep({ 
        number: i + 100, 
        title: `${query} PEP ${i + 1}` 
      })
    ),
    total: count,
    query,
  }),
}

/**
 * Performance testing utilities.
 */
export const performanceUtils = {
  /**
   * Measure render time of a component.
   */
  measureRenderTime: async (renderFn: () => any) => {
    const start = performance.now()
    await renderFn()
    const end = performance.now()
    return end - start
  },
  
  /**
   * Assert that a render completes within a time limit.
   */
  assertRenderPerformance: async (renderFn: () => any, maxMs = 100) => {
    const duration = await performanceUtils.measureRenderTime(renderFn)
    if (duration > maxMs) {
      throw new Error(`Render took ${duration}ms, expected max ${maxMs}ms`)
    }
    return duration
  },
}

/**
 * Accessibility testing utilities.
 */
export const a11yUtils = {
  /**
   * Check if an element has proper ARIA attributes.
   */
  hasProperAria: (element: HTMLElement) => {
    // Basic checks for common ARIA patterns
    const hasRole = element.hasAttribute('role')
    const hasLabel = element.hasAttribute('aria-label') || element.hasAttribute('aria-labelledby')
    const hasDescription = element.hasAttribute('aria-describedby')
    
    return {
      hasRole,
      hasLabel,
      hasDescription,
      isAccessible: hasRole && hasLabel,
    }
  },
  
  /**
   * Check if an element is keyboard accessible.
   */
  isKeyboardAccessible: (element: HTMLElement) => {
    const isInteractive = ['button', 'a', 'input', 'select', 'textarea'].includes(
      element.tagName.toLowerCase()
    )
    const hasTabIndex = element.hasAttribute('tabindex')
    const tabIndex = element.getAttribute('tabindex')
    
    return {
      isInteractive,
      hasTabIndex,
      tabIndex,
      isAccessible: isInteractive || (hasTabIndex && tabIndex !== '-1'),
    }
  },
}

// Re-export everything from React Testing Library for convenience
export * from '@testing-library/react'
export { renderWithProviders as render }
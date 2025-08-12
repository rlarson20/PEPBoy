/**
 * Global test setup configuration.
 * 
 * This file is executed before each test file and sets up:
 * - Jest DOM matchers for React Testing Library
 * - Mock Service Worker (MSW) configuration
 * - Global test utilities and polyfills
 * - Custom test assertions
 */

import '@testing-library/jest-dom'
import { expect, afterEach, beforeAll, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import { setupServer } from 'msw/node'
import { rest } from 'msw'

// Clean up after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup()
})

// Mock Service Worker setup for API mocking
const mockApiBaseUrl = 'http://localhost:8000/api'

// Default handlers for common API endpoints
const defaultHandlers = [
  // Mock PEP listing endpoint
  rest.get(`${mockApiBaseUrl}/peps`, (req, res, ctx) => {
    const skip = req.url.searchParams.get('skip') || '0'
    const limit = req.url.searchParams.get('limit') || '10'
    
    return res(
      ctx.status(200),
      ctx.json({
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
        skip: parseInt(skip),
        limit: parseInt(limit)
      })
    )
  }),

  // Mock individual PEP endpoint
  rest.get(`${mockApiBaseUrl}/peps/:pepNumber`, (req, res, ctx) => {
    const { pepNumber } = req.params
    
    if (pepNumber === '1') {
      return res(
        ctx.status(200),
        ctx.json({
          number: 1,
          title: 'PEP Purpose and Guidelines',
          status: 'Active',
          type: 'Process',
          topic: 'Core',
          created: '2000-06-13',
          url: 'https://peps.python.org/pep-0001/',
          authors: ['Barry Warsaw', 'Jeremy Hylton'],
          content: 'This PEP contains the index of all Python Enhancement Proposals...'
        })
      )
    }
    
    return res(
      ctx.status(404),
      ctx.json({ detail: 'PEP not found' })
    )
  }),

  // Mock search endpoint
  rest.get(`${mockApiBaseUrl}/peps/search`, (req, res, ctx) => {
    const query = req.url.searchParams.get('q') || ''
    
    return res(
      ctx.status(200),
      ctx.json({
        peps: [
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
        total: 1,
        query
      })
    )
  }),

  // Mock error endpoint for testing error handling
  rest.get(`${mockApiBaseUrl}/error`, (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({ detail: 'Internal server error' })
    )
  })
]

// Create MSW server instance
export const server = setupServer(...defaultHandlers)

// Establish API mocking before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' })
})

// Reset any runtime handlers after each test
afterEach(() => {
  server.resetHandlers()
})

// Clean up after all tests are done
afterAll(() => {
  server.close()
})

// Custom matchers
expect.extend({
  toBeInTheDocument: (received) => {
    const pass = received && received.parentElement
    return {
      message: () => `expected element ${pass ? 'not ' : ''}to be in the document`,
      pass,
    }
  },
})

// Global test configuration
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {
    return null
  }
  disconnect() {
    return null
  }
  unobserve() {
    return null
  }
}

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {
    return null
  }
  disconnect() {
    return null
  }
  unobserve() {
    return null
  }
}

// Console error suppression for expected test errors
const originalError = console.error
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render is no longer supported') ||
       args[0].includes('Warning: An invalid form control'))
    ) {
      return
    }
    originalError.call(console, ...args)
  }
})

afterAll(() => {
  console.error = originalError
})

// Global test timeout increase for slower tests
import { vi } from 'vitest'
vi.setConfig({ testTimeout: 10000 })
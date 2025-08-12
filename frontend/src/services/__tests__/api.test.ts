/**
 * Unit tests for API service.
 * 
 * This demonstrates TDD methodology for service layer testing:
 * - Mocking HTTP requests and responses
 * - Testing error handling and edge cases
 * - Validating request parameters and response processing
 * - Testing retry logic and timeout handling
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { mockAxiosResponse } from '../../test-utils/test-utils'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

// Import the API functions (these need to be implemented)
import { 
  fetchPeps, 
  fetchPepById, 
  searchPeps,
  // These would be the actual functions from api.ts
} from '../api'

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset axios create mock
    mockedAxios.create.mockReturnValue(mockedAxios)
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('fetchPeps', () => {
    it('should fetch PEPs with default parameters', async () => {
      // TDD Red: This test will fail until fetchPeps is implemented
      const mockResponse = mockAxiosResponse({
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
          }
        ],
        total: 1,
        page: 1,
        per_page: 10
      })

      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      const result = await fetchPeps()

      expect(mockedAxios.get).toHaveBeenCalledWith('/peps', {
        params: {
          page: 1,
          per_page: 10
        }
      })
      expect(result).toEqual(mockResponse.data)
    })

    it('should fetch PEPs with custom parameters', async () => {
      const mockResponse = mockAxiosResponse({
        peps: [],
        total: 0,
        page: 2,
        per_page: 20
      })

      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      const params = {
        page: 2,
        per_page: 20,
        status: 'Final',
        type: 'Standards Track'
      }

      await fetchPeps(params)

      expect(mockedAxios.get).toHaveBeenCalledWith('/peps', {
        params
      })
    })

    it('should handle pagination correctly', async () => {
      const page1Response = mockAxiosResponse({
        peps: [{ number: 1, title: 'PEP 1' }],
        total: 25,
        page: 1,
        per_page: 10
      })

      const page2Response = mockAxiosResponse({
        peps: [{ number: 2, title: 'PEP 2' }],
        total: 25,
        page: 2,
        per_page: 10
      })

      mockedAxios.get
        .mockResolvedValueOnce(page1Response)
        .mockResolvedValueOnce(page2Response)

      const result1 = await fetchPeps({ page: 1, per_page: 10 })
      const result2 = await fetchPeps({ page: 2, per_page: 10 })

      expect(result1.page).toBe(1)
      expect(result2.page).toBe(2)
      expect(result1.total).toBe(25)
      expect(result2.total).toBe(25)
    })

    it('should handle network errors', async () => {
      const networkError = new Error('Network error - please check your connection')
      mockedAxios.get.mockRejectedValueOnce({
        request: {},
        message: 'Network Error'
      })

      await expect(fetchPeps()).rejects.toThrow('Network error - please check your connection')
    })

    it('should handle API errors with proper error messages', async () => {
      const apiError = {
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      }
      mockedAxios.get.mockRejectedValueOnce(apiError)

      await expect(fetchPeps()).rejects.toThrow('API Error: 500 - Internal server error')
    })

    it('should handle timeout errors', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        code: 'ECONNABORTED',
        message: 'timeout of 10000ms exceeded'
      })

      await expect(fetchPeps()).rejects.toThrow('Request failed')
    })
  })

  describe('fetchPepById', () => {
    it('should fetch single PEP by ID', async () => {
      const mockPep = {
        number: 8,
        title: 'Style Guide for Python Code',
        status: 'Active',
        type: 'Process',
        topic: 'Core',
        created: '2001-07-05',
        content: 'This document gives coding conventions...',
        authors: ['Guido van Rossum', 'Barry Warsaw']
      }

      const mockResponse = mockAxiosResponse(mockPep)
      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      const result = await fetchPepById(8)

      expect(mockedAxios.get).toHaveBeenCalledWith('/peps/8')
      expect(result).toEqual(mockPep)
    })

    it('should handle PEP not found (404)', async () => {
      const notFoundError = {
        response: {
          status: 404,
          data: { detail: 'PEP not found' }
        }
      }
      mockedAxios.get.mockRejectedValueOnce(notFoundError)

      await expect(fetchPepById(9999)).rejects.toThrow('API Error: 404 - PEP not found')
    })

    it('should validate PEP ID parameter', async () => {
      // Should reject invalid PEP IDs
      await expect(fetchPepById(-1)).rejects.toThrow('Invalid PEP ID')
      await expect(fetchPepById(0)).rejects.toThrow('Invalid PEP ID')
      await expect(fetchPepById(null as any)).rejects.toThrow('Invalid PEP ID')
      await expect(fetchPepById(undefined as any)).rejects.toThrow('Invalid PEP ID')
    })

    it('should handle string PEP IDs by converting to number', async () => {
      const mockResponse = mockAxiosResponse({ number: 123, title: 'Test PEP' })
      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      await fetchPepById('123' as any)

      expect(mockedAxios.get).toHaveBeenCalledWith('/peps/123')
    })
  })

  describe('searchPeps', () => {
    it('should search PEPs with query string', async () => {
      const mockSearchResults = {
        results: [
          {
            number: 484,
            title: 'Type Hints',
            status: 'Final',
            type: 'Standards Track',
            topic: 'Typing'
          }
        ],
        query: 'type hints',
        total_matches: 1
      }

      const mockResponse = mockAxiosResponse(mockSearchResults)
      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      const result = await searchPeps({ q: 'type hints' })

      expect(mockedAxios.get).toHaveBeenCalledWith('/peps/search', {
        params: { q: 'type hints', page: 1 }
      })
      expect(result).toEqual(mockSearchResults)
    })

    it('should handle empty search query', async () => {
      await expect(searchPeps({ q: '' })).rejects.toThrow('Search query cannot be empty')
      await expect(searchPeps({ q: '   ' })).rejects.toThrow('Search query cannot be empty')
    })

    it('should handle search with pagination', async () => {
      const mockResponse = mockAxiosResponse({
        results: [],
        query: 'async',
        total_matches: 15
      })

      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      await searchPeps({ q: 'async', page: 2 })

      expect(mockedAxios.get).toHaveBeenCalledWith('/peps/search', {
        params: { q: 'async', page: 2 }
      })
    })

    it('should handle no search results', async () => {
      const mockResponse = mockAxiosResponse({
        results: [],
        query: 'nonexistent',
        total_matches: 0
      })

      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      const result = await searchPeps({ q: 'nonexistent' })

      expect(result.results).toHaveLength(0)
      expect(result.total_matches).toBe(0)
    })

    it('should escape special characters in search query', async () => {
      const mockResponse = mockAxiosResponse({
        results: [],
        query: 'test & special',
        total_matches: 0
      })

      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      await searchPeps({ q: 'test & special' })

      expect(mockedAxios.get).toHaveBeenCalledWith('/peps/search', {
        params: { q: 'test & special', page: 1 }
      })
    })
  })

  describe('API Configuration', () => {
    it('should use correct base URL from environment', () => {
      // Mock environment variable
      import.meta.env = { VITE_API_URL: 'https://api.example.com' }

      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: 'https://api.example.com'
        })
      )
    })

    it('should use default base URL when environment variable is not set', () => {
      import.meta.env = {}

      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: 'http://localhost:8420/api'
        })
      )
    })

    it('should set appropriate timeout', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 10000
        })
      )
    })

    it('should set correct headers', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: {
            'Content-Type': 'application/json'
          }
        })
      )
    })
  })

  describe('Request Interceptors', () => {
    it('should add request interceptors for authentication', async () => {
      // Mock authentication token
      const mockToken = 'mock-auth-token'
      localStorage.setItem('authToken', mockToken)

      const mockResponse = mockAxiosResponse({ peps: [] })
      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      await fetchPeps()

      // Should have added Authorization header
      expect(mockedAxios.get).toHaveBeenCalledWith('/peps', 
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${mockToken}`
          })
        })
      )

      localStorage.removeItem('authToken')
    })

    it('should add correlation ID to requests', async () => {
      const mockResponse = mockAxiosResponse({ peps: [] })
      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      await fetchPeps()

      expect(mockedAxios.get).toHaveBeenCalledWith('/peps',
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Correlation-ID': expect.any(String)
          })
        })
      )
    })
  })

  describe('Response Interceptors', () => {
    it('should transform response data correctly', async () => {
      const rawResponse = {
        data: {
          items: [{ number: 1, title: 'Test' }],
          pagination: { total: 1, page: 1, per_page: 10 }
        }
      }

      mockedAxios.get.mockResolvedValueOnce(rawResponse)

      const result = await fetchPeps()

      // Should transform to expected format
      expect(result).toEqual({
        peps: rawResponse.data.items,
        total: rawResponse.data.pagination.total,
        page: rawResponse.data.pagination.page,
        per_page: rawResponse.data.pagination.per_page
      })
    })

    it('should handle malformed response data', async () => {
      const malformedResponse = {
        data: null
      }

      mockedAxios.get.mockResolvedValueOnce(malformedResponse)

      await expect(fetchPeps()).rejects.toThrow('Invalid response format')
    })
  })

  describe('Retry Logic', () => {
    it('should retry failed requests', async () => {
      const networkError = { request: {}, message: 'Network Error' }
      const successResponse = mockAxiosResponse({ peps: [] })

      mockedAxios.get
        .mockRejectedValueOnce(networkError)
        .mockRejectedValueOnce(networkError)
        .mockResolvedValueOnce(successResponse)

      const result = await fetchPeps()

      expect(mockedAxios.get).toHaveBeenCalledTimes(3)
      expect(result).toEqual(successResponse.data)
    })

    it('should not retry client errors (4xx)', async () => {
      const clientError = {
        response: {
          status: 400,
          data: { message: 'Bad request' }
        }
      }

      mockedAxios.get.mockRejectedValueOnce(clientError)

      await expect(fetchPeps()).rejects.toThrow('API Error: 400 - Bad request')
      expect(mockedAxios.get).toHaveBeenCalledTimes(1)
    })

    it('should respect maximum retry attempts', async () => {
      const networkError = { request: {}, message: 'Network Error' }

      mockedAxios.get.mockRejectedValue(networkError)

      await expect(fetchPeps()).rejects.toThrow('Network error - please check your connection')
      expect(mockedAxios.get).toHaveBeenCalledTimes(3) // Initial + 2 retries
    })
  })

  describe('Caching', () => {
    it('should cache GET requests', async () => {
      const mockResponse = mockAxiosResponse({ number: 1, title: 'Cached PEP' })
      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      // First request
      const result1 = await fetchPepById(1)
      
      // Second request should return cached result
      const result2 = await fetchPepById(1)

      expect(mockedAxios.get).toHaveBeenCalledTimes(1)
      expect(result1).toEqual(result2)
    })

    it('should respect cache expiration', async () => {
      const mockResponse = mockAxiosResponse({ number: 1, title: 'Fresh PEP' })
      mockedAxios.get.mockResolvedValue(mockResponse)

      // Mock cache expiration (5 minutes)
      const fiveMinutesLater = Date.now() + 5 * 60 * 1000
      vi.setSystemTime(fiveMinutesLater)

      await fetchPepById(1)
      await fetchPepById(1) // Should make new request due to expiration

      expect(mockedAxios.get).toHaveBeenCalledTimes(2)
    })

    it('should invalidate cache on errors', async () => {
      const successResponse = mockAxiosResponse({ number: 1, title: 'Success' })
      const errorResponse = { response: { status: 500 } }

      mockedAxios.get
        .mockResolvedValueOnce(successResponse)
        .mockRejectedValueOnce(errorResponse)
        .mockResolvedValueOnce(successResponse)

      await fetchPepById(1) // Success, cached
      await expect(fetchPepById(1)).rejects.toThrow() // Error, cache invalidated
      await fetchPepById(1) // Should make new request

      expect(mockedAxios.get).toHaveBeenCalledTimes(3)
    })
  })

  describe('TypeScript Type Safety', () => {
    it('should enforce correct parameter types', () => {
      // These should cause TypeScript errors in a real implementation
      
      // @ts-expect-error - page should be number
      expect(() => fetchPeps({ page: 'invalid' })).toThrow()
      
      // @ts-expect-error - pepId should be number
      expect(() => fetchPepById('not-a-number')).toThrow()
      
      // @ts-expect-error - q is required
      expect(() => searchPeps({})).toThrow()
    })

    it('should return correctly typed responses', async () => {
      const mockResponse = mockAxiosResponse({
        peps: [{ number: 1, title: 'Test', status: 'Active' }],
        total: 1,
        page: 1,
        per_page: 10
      })

      mockedAxios.get.mockResolvedValueOnce(mockResponse)

      const result = await fetchPeps()

      // TypeScript should infer correct types
      expect(typeof result.total).toBe('number')
      expect(typeof result.page).toBe('number')
      expect(Array.isArray(result.peps)).toBe(true)
      
      if (result.peps.length > 0) {
        expect(typeof result.peps[0].number).toBe('number')
        expect(typeof result.peps[0].title).toBe('string')
      }
    })
  })
})
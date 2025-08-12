/**
 * Unit tests for SearchBar component.
 * 
 * This demonstrates TDD red-green-refactor methodology for React components:
 * 1. Red: Write failing tests that define the expected behavior
 * 2. Green: Implement minimal code to make tests pass
 * 3. Refactor: Improve code while keeping tests passing
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, createMockRouterHooks } from '../../test-utils/test-utils'
import SearchBar from '../SearchBar'

// Mock router hooks since SearchBar likely uses navigation
const mockRouterHooks = createMockRouterHooks()
vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useNavigate: () => mockRouterHooks.useNavigate,
  useSearchParams: () => mockRouterHooks.useSearchParams,
}))

describe('SearchBar Component', () => {
  const user = userEvent.setup()
  
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Component Rendering', () => {
    it('should render search input field', () => {
      // TDD Red: This test will fail until SearchBar is implemented
      renderWithProviders(<SearchBar />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      expect(searchInput).toBeInTheDocument()
      expect(searchInput).toHaveAttribute('type', 'text')
    })

    it('should render search button', () => {
      renderWithProviders(<SearchBar />)
      
      const searchButton = screen.getByRole('button', { name: /search/i })
      expect(searchButton).toBeInTheDocument()
      expect(searchButton).toHaveAttribute('type', 'submit')
    })

    it('should have placeholder text', () => {
      renderWithProviders(<SearchBar />)
      
      const searchInput = screen.getByPlaceholderText(/search for peps/i)
      expect(searchInput).toBeInTheDocument()
    })

    it('should be accessible with proper ARIA attributes', () => {
      renderWithProviders(<SearchBar />)
      
      const searchInput = screen.getByRole('textbox', { name: /search peps/i })
      expect(searchInput).toBeInTheDocument()
      expect(searchInput).toHaveAccessibleName()
    })
  })

  describe('User Interactions', () => {
    it('should update input value when user types', async () => {
      renderWithProviders(<SearchBar />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      const testQuery = 'type hints'
      
      await user.type(searchInput, testQuery)
      
      expect(searchInput).toHaveValue(testQuery)
    })

    it('should call onSearch when form is submitted', async () => {
      const mockOnSearch = vi.fn()
      renderWithProviders(<SearchBar onSearch={mockOnSearch} />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      const searchButton = screen.getByRole('button', { name: /search/i })
      
      await user.type(searchInput, 'python')
      await user.click(searchButton)
      
      expect(mockOnSearch).toHaveBeenCalledWith('python')
    })

    it('should call onSearch when Enter key is pressed', async () => {
      const mockOnSearch = vi.fn()
      renderWithProviders(<SearchBar onSearch={mockOnSearch} />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      
      await user.type(searchInput, 'async')
      await user.keyboard('{Enter}')
      
      expect(mockOnSearch).toHaveBeenCalledWith('async')
    })

    it('should not submit empty search', async () => {
      const mockOnSearch = vi.fn()
      renderWithProviders(<SearchBar onSearch={mockOnSearch} />)
      
      const searchButton = screen.getByRole('button', { name: /search/i })
      await user.click(searchButton)
      
      expect(mockOnSearch).not.toHaveBeenCalled()
    })

    it('should trim whitespace from search query', async () => {
      const mockOnSearch = vi.fn()
      renderWithProviders(<SearchBar onSearch={mockOnSearch} />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      
      await user.type(searchInput, '  python  ')
      await user.keyboard('{Enter}')
      
      expect(mockOnSearch).toHaveBeenCalledWith('python')
    })
  })

  describe('Search State Management', () => {
    it('should show loading state during search', async () => {
      const slowOnSearch = vi.fn(() => new Promise(resolve => setTimeout(resolve, 100)))
      renderWithProviders(<SearchBar onSearch={slowOnSearch} isLoading={true} />)
      
      const searchButton = screen.getByRole('button', { name: /search/i })
      expect(searchButton).toBeDisabled()
      
      // Should show loading indicator
      expect(screen.getByTestId('search-loading')).toBeInTheDocument()
    })

    it('should clear search when clear button is clicked', async () => {
      renderWithProviders(<SearchBar />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      
      // Type something first
      await user.type(searchInput, 'test query')
      expect(searchInput).toHaveValue('test query')
      
      // Click clear button
      const clearButton = screen.getByRole('button', { name: /clear search/i })
      await user.click(clearButton)
      
      expect(searchInput).toHaveValue('')
    })

    it('should preserve search value from URL parameters', () => {
      // Mock URLSearchParams to return initial search value
      const mockSearchParams = new URLSearchParams('?q=existing-search')
      mockRouterHooks.useSearchParams.mockReturnValue([mockSearchParams, vi.fn()])
      
      renderWithProviders(<SearchBar />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      expect(searchInput).toHaveValue('existing-search')
    })
  })

  describe('Keyboard Navigation', () => {
    it('should be keyboard accessible', async () => {
      renderWithProviders(<SearchBar />)
      
      // Tab to search input
      await user.tab()
      expect(screen.getByLabelText(/search peps/i)).toHaveFocus()
      
      // Tab to search button
      await user.tab()
      expect(screen.getByRole('button', { name: /search/i })).toHaveFocus()
    })

    it('should support keyboard shortcuts', async () => {
      const mockOnSearch = vi.fn()
      renderWithProviders(<SearchBar onSearch={mockOnSearch} />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      
      // Test Ctrl+Enter for quick search
      await user.type(searchInput, 'shortcuts')
      await user.keyboard('{Control>}{Enter}{/Control}')
      
      expect(mockOnSearch).toHaveBeenCalledWith('shortcuts')
    })
  })

  describe('Search Suggestions', () => {
    it('should show recent searches dropdown', async () => {
      const recentSearches = ['python', 'async', 'typing']
      renderWithProviders(<SearchBar recentSearches={recentSearches} />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      await user.click(searchInput)
      
      // Should show dropdown with recent searches
      const dropdown = screen.getByRole('listbox', { name: /recent searches/i })
      expect(dropdown).toBeInTheDocument()
      
      recentSearches.forEach(search => {
        expect(screen.getByRole('option', { name: search })).toBeInTheDocument()
      })
    })

    it('should select suggestion when clicked', async () => {
      const mockOnSearch = vi.fn()
      const recentSearches = ['python', 'async']
      
      renderWithProviders(
        <SearchBar onSearch={mockOnSearch} recentSearches={recentSearches} />
      )
      
      const searchInput = screen.getByLabelText(/search peps/i)
      await user.click(searchInput)
      
      const suggestion = screen.getByRole('option', { name: 'python' })
      await user.click(suggestion)
      
      expect(searchInput).toHaveValue('python')
      expect(mockOnSearch).toHaveBeenCalledWith('python')
    })

    it('should navigate suggestions with arrow keys', async () => {
      const recentSearches = ['python', 'async', 'typing']
      renderWithProviders(<SearchBar recentSearches={recentSearches} />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      await user.click(searchInput)
      
      // Arrow down should highlight first suggestion
      await user.keyboard('{ArrowDown}')
      expect(screen.getByRole('option', { name: 'python' })).toHaveClass('highlighted')
      
      // Arrow down again should highlight second suggestion
      await user.keyboard('{ArrowDown}')
      expect(screen.getByRole('option', { name: 'async' })).toHaveClass('highlighted')
      
      // Enter should select highlighted suggestion
      await user.keyboard('{Enter}')
      expect(searchInput).toHaveValue('async')
    })
  })

  describe('Error Handling', () => {
    it('should display error message when search fails', () => {
      const errorMessage = 'Search service unavailable'
      renderWithProviders(<SearchBar error={errorMessage} />)
      
      const errorElement = screen.getByRole('alert')
      expect(errorElement).toHaveTextContent(errorMessage)
      expect(errorElement).toHaveClass('error-message')
    })

    it('should clear error when new search is initiated', async () => {
      const mockOnSearch = vi.fn()
      renderWithProviders(
        <SearchBar onSearch={mockOnSearch} error="Previous error" />
      )
      
      const searchInput = screen.getByLabelText(/search peps/i)
      await user.type(searchInput, 'new search')
      
      // Error should be cleared when typing starts
      await waitFor(() => {
        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      })
    })
  })

  describe('Responsive Design', () => {
    it('should adapt to mobile viewport', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })
      
      renderWithProviders(<SearchBar />)
      
      const searchContainer = screen.getByTestId('search-container')
      expect(searchContainer).toHaveClass('mobile-layout')
    })

    it('should show compact button text on small screens', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 320,
      })
      
      renderWithProviders(<SearchBar />)
      
      const searchButton = screen.getByRole('button', { name: /search/i })
      expect(searchButton).toHaveTextContent('🔍') // Icon instead of text
    })
  })

  describe('Performance', () => {
    it('should debounce search input', async () => {
      const mockOnSearch = vi.fn()
      renderWithProviders(<SearchBar onSearch={mockOnSearch} enableLiveSearch={true} />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      
      // Type multiple characters quickly
      await user.type(searchInput, 'python', { delay: 50 })
      
      // Should not call onSearch immediately
      expect(mockOnSearch).not.toHaveBeenCalled()
      
      // Should call onSearch after debounce delay
      await waitFor(() => {
        expect(mockOnSearch).toHaveBeenCalledWith('python')
      }, { timeout: 1000 })
      
      // Should only be called once, not for each character
      expect(mockOnSearch).toHaveBeenCalledTimes(1)
    })

    it('should cancel previous search requests', async () => {
      const mockOnSearch = vi.fn()
      renderWithProviders(<SearchBar onSearch={mockOnSearch} />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      
      // Start first search
      await user.type(searchInput, 'first')
      await user.keyboard('{Enter}')
      
      // Immediately start second search
      await user.clear(searchInput)
      await user.type(searchInput, 'second')
      await user.keyboard('{Enter}')
      
      // Should cancel first search and only complete second
      await waitFor(() => {
        expect(mockOnSearch).toHaveBeenLastCalledWith('second')
      })
    })
  })

  describe('Integration', () => {
    it('should integrate with router for navigation', async () => {
      const mockOnSearch = vi.fn()
      renderWithProviders(<SearchBar onSearch={mockOnSearch} />)
      
      const searchInput = screen.getByLabelText(/search peps/i)
      await user.type(searchInput, 'routing test')
      await user.keyboard('{Enter}')
      
      // Should update URL search parameters
      expect(mockRouterHooks.useNavigate).toHaveBeenCalledWith({
        pathname: '/search',
        search: '?q=routing+test'
      })
    })

    it('should work within form context', async () => {
      const mockOnSubmit = vi.fn()
      
      renderWithProviders(
        <form onSubmit={mockOnSubmit}>
          <SearchBar />
          <button type="submit">Submit Form</button>
        </form>
      )
      
      const searchInput = screen.getByLabelText(/search peps/i)
      const submitButton = screen.getByRole('button', { name: /submit form/i })
      
      await user.type(searchInput, 'form test')
      await user.click(submitButton)
      
      expect(mockOnSubmit).toHaveBeenCalled()
    })
  })
})
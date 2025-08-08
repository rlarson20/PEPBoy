## Step-by-Step Implementation Plan

### 1. Project Setup (DONE)

```bash
npm create vite@latest pep-viewer --template react-ts
cd pep-viewer
npm install react-router-dom axios dompurify
npm install -D @types/dompurify
```

### 2. Create API Service Layer

Create `src/services/api.ts`:

- Define TypeScript interfaces for PEP data structures
- Implement functions: `fetchPeps()`, `fetchPepById()`, `searchPeps()`
- Configure axios base URL and error handling

### 3. Set Up Routing Structure

In `src/App.tsx`:

- Import `BrowserRouter`, `Routes`, `Route` from react-router-dom
- Define your three main routes
- Wrap everything in `<BrowserRouter>`

### 4. Build Core Components (Bottom-Up)

**Start with leaf components:**

- `Header.tsx` - navigation links, logo
- `Footer.tsx` - static content
- `SearchBar.tsx` - input field, submit handler
- `PepListItem.tsx` - individual PEP summary display

**Then container components:**

- `Layout.tsx` - combines Header, Footer, renders children
- `PepList.tsx` - maps over PEP array, renders PepListItem components
- `PaginationControls.tsx` - prev/next buttons, page numbers

### 5. Build Page Components

- `HomePage.tsx` - fetches PEP list, handles filters/pagination
- `PepDetailPage.tsx` - fetches single PEP, sanitizes HTML with DOMPurify
- `SearchResultsPage.tsx` - handles search query from URL params

### 6. Wire Up Data Flow

- Add `useState` and `useEffect` hooks to fetch data
- Handle loading states and errors in each page component
- Connect search functionality between SearchBar and results page

### 7. Test Navigation

- Verify all routes work
- Test URL parameters capture correctly
- Ensure back/forward browser buttons work

This order ensures you build dependencies first and can test incrementally as you add each piece.

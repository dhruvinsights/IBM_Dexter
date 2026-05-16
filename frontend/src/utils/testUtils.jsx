/**
 * Test Utilities for IBM Dexter Frontend
 * Provides custom render functions and helpers for testing React components
 */

import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Theme } from '@carbon/react';
import PropTypes from 'prop-types';

/**
 * Custom render function that wraps components with necessary providers
 * @param {React.ReactElement} ui - Component to render
 * @param {Object} options - Render options
 * @param {string} options.theme - Carbon theme ('white', 'g10', 'g90', 'g100')
 * @param {string} options.route - Initial route for router
 * @param {Object} options.renderOptions - Additional options for @testing-library/react render
 * @returns {Object} Render result from @testing-library/react
 */
export function renderWithProviders(ui, options = {}) {
  const {
    theme = 'g100',
    route = '/',
    ...renderOptions
  } = options;

  // Set initial route
  window.history.pushState({}, 'Test page', route);

  function Wrapper({ children }) {
    return (
      <BrowserRouter>
        <Theme theme={theme}>
          {children}
        </Theme>
      </BrowserRouter>
    );
  }

  Wrapper.propTypes = {
    children: PropTypes.node.isRequired,
  };

  return render(ui, { wrapper: Wrapper, ...renderOptions });
}

/**
 * Custom render for components that don't need routing
 * @param {React.ReactElement} ui - Component to render
 * @param {Object} options - Render options
 * @param {string} options.theme - Carbon theme
 * @param {Object} options.renderOptions - Additional options
 * @returns {Object} Render result
 */
export function renderWithTheme(ui, options = {}) {
  const { theme = 'g100', ...renderOptions } = options;

  function Wrapper({ children }) {
    return <Theme theme={theme}>{children}</Theme>;
  }

  Wrapper.propTypes = {
    children: PropTypes.node.isRequired,
  };

  return render(ui, { wrapper: Wrapper, ...renderOptions });
}

/**
 * Wait for an element to be removed from the DOM
 * @param {Function} callback - Function that queries for the element
 * @param {Object} options - Wait options
 * @returns {Promise} Promise that resolves when element is removed
 */
export async function waitForElementToBeRemoved(callback, options = {}) {
  const { timeout = 3000 } = options;
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    try {
      callback();
      await new Promise(resolve => setTimeout(resolve, 50));
    } catch (error) {
      // Element not found, it's been removed
      return;
    }
  }

  throw new Error('Element was not removed within timeout');
}

/**
 * Create mock data for testing
 */
export const mockData = {
  pullRequest: {
    id: 1,
    title: 'Test PR',
    number: 123,
    author: 'testuser',
    status: 'open',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
  
  review: {
    id: 1,
    pull_request_id: 1,
    status: 'completed',
    score: 85,
    findings: [],
    created_at: '2024-01-01T00:00:00Z',
  },
  
  repository: {
    id: 1,
    name: 'test-repo',
    full_name: 'org/test-repo',
    url: 'https://github.com/org/test-repo',
    language: 'JavaScript',
  },
  
  user: {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    role: 'developer',
  },
};

/**
 * Mock API responses
 */
export const mockApiResponses = {
  success: (data) => ({
    ok: true,
    status: 200,
    json: async () => data,
  }),
  
  error: (message = 'API Error', status = 500) => ({
    ok: false,
    status,
    json: async () => ({ error: message }),
  }),
  
  loading: () => new Promise(() => {}), // Never resolves
};

/**
 * Create a mock fetch function
 * @param {Object} responses - Map of URL patterns to responses
 * @returns {Function} Mock fetch function
 */
export function createMockFetch(responses = {}) {
  return async (url, options = {}) => {
    const matchedKey = Object.keys(responses).find(key => url.includes(key));
    
    if (matchedKey) {
      const response = responses[matchedKey];
      if (typeof response === 'function') {
        return response(url, options);
      }
      return mockApiResponses.success(response);
    }
    
    return mockApiResponses.error('Not found', 404);
  };
}

/**
 * Simulate user typing
 * @param {HTMLElement} element - Input element
 * @param {string} text - Text to type
 */
export async function typeText(element, text) {
  const { fireEvent } = await import('@testing-library/react');
  
  element.focus();
  
  for (const char of text) {
    fireEvent.change(element, {
      target: { value: element.value + char },
    });
    await new Promise(resolve => setTimeout(resolve, 10));
  }
}

/**
 * Wait for async updates
 * @param {number} ms - Milliseconds to wait
 * @returns {Promise} Promise that resolves after delay
 */
export const waitFor = (ms = 0) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Create a mock IntersectionObserver
 * @returns {Object} Mock IntersectionObserver
 */
export function createMockIntersectionObserver() {
  const observers = new Map();
  
  return class MockIntersectionObserver {
    constructor(callback) {
      this.callback = callback;
      this.elements = new Set();
    }
    
    observe(element) {
      this.elements.add(element);
      observers.set(element, this);
    }
    
    unobserve(element) {
      this.elements.delete(element);
      observers.delete(element);
    }
    
    disconnect() {
      this.elements.clear();
    }
    
    static trigger(element, isIntersecting) {
      const observer = observers.get(element);
      if (observer) {
        observer.callback([{ target: element, isIntersecting }]);
      }
    }
  };
}

// Re-export everything from @testing-library/react
export * from '@testing-library/react';

// Re-export userEvent
export { default as userEvent } from '@testing-library/user-event';

// Made with Bob

// Jest setup file for React Testing Library
import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock sessionStorage
const sessionStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = jest.fn();

// Mock IntersectionObserver
class MockIntersectionObserver {
  readonly root: Element | null = null;
  readonly rootMargin: string = '';
  readonly thresholds: ReadonlyArray<number> = [];

  constructor(public callback: IntersectionObserverCallback) {
    void callback;
  }

  observe() {
    return undefined;
  }
  unobserve() {
    return undefined;
  }
  disconnect() {
    return undefined;
  }
  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }
}

Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  configurable: true,
  value: MockIntersectionObserver,
});

// Mock ResizeObserver
class MockResizeObserver {
  constructor(public callback: ResizeObserverCallback) {
    void callback;
  }
  observe() {
    return undefined;
  }
  unobserve() {
    return undefined;
  }
  disconnect() {
    return undefined;
  }
}

Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  configurable: true,
  value: MockResizeObserver,
});

// Add a global mock for fetch with safe defaults.
// Individual tests can override `global.fetch.mockResolvedValueOnce(...)` as needed.
const mockFetch = jest.fn().mockImplementation((input: RequestInfo, init?: RequestInit) => {
  const url = typeof input === 'string' ? input : (input as any)?.url || '';
  const method = (init?.method || 'GET').toUpperCase();

  const ok = true;
  const status = 200;

  let payload: any = {};
  if (url.includes('/api/v2/mood/recent')) payload = { ok: true, items: [] };
  else if (url.includes('/api/v2/mood/log') && method === 'POST') payload = { ok: true };
  else if (url.includes('/api/v2/journal/append') && method === 'POST')
    payload = { ok: true, stored: true };
  else if (url.includes('/api/v2/thought-record/create') && method === 'POST')
    payload = { ok: true, record: { id: 't', ts: 0 } };
  else if (url.includes('/api/v2/safety-plan') && method === 'GET')
    payload = { ok: true, plan: null };
  else if (url.includes('/api/v2/safety-plan') && method === 'POST')
    payload = { ok: true, saved: true };
  else if (url.includes('/resources/api/crisis')) payload = { resources: [] };
  else if (url.includes('/api/v2/export/text')) payload = { ok: true, text: '' };
  else if (url.includes('/api/v1/chat') && method === 'POST') payload = { response: 'ok' };

  const body = JSON.stringify(payload);

  return Promise.resolve({
    ok,
    status,
    text: async () => body,
    json: async () => payload,
  } as any);
});
global.fetch = mockFetch as unknown as typeof window.fetch;

// Add a global mock for requestIdleCallback
window.requestIdleCallback = (fn) => {
  const start = Date.now();
  return setTimeout(() => {
    fn({
      didTimeout: false,
      timeRemaining: () => Math.max(0, 50 - (Date.now() - start)),
    });
  }, 1) as unknown as number;
};

window.cancelIdleCallback = (id) => {
  clearTimeout(id);
};

// Mock console methods in test environment
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeAll(() => {
  // Mock console.error to fail tests on React warnings
  console.error = (...args) => {
    originalConsoleError(...args);
    throw new Error('Console error was called. This is often caused by a React warning.');
  };

  // Mock console.warn to fail tests on React warnings
  console.warn = (...args) => {
    const msg = String(args[0] ?? '');
    // React Router v6 emits a known "future flag" warning at runtime.
    // This is not actionable for unit tests, and failing tests on it is noisy.
    if (msg.includes('React Router Future Flag Warning')) {
      return;
    }
    originalConsoleWarn(...args);
    throw new Error('Console warn was called. This is often caused by a React warning.');
  };
});

afterAll(() => {
  // Restore original console methods
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
});

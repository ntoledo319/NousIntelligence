import React, { ReactElement } from 'react';
import { render, RenderOptions, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';
import { BrowserRouter } from 'react-router-dom';

// Mock these imports for tests
// Once these modules are created, these mocks can be removed
const QueryClientProvider = ({ children }: { children: React.ReactNode }) => <>{children}</>;

// Mock theme until it's created
const theme = {
  colors: {
    primary: '#0070f3',
    white: '#ffffff',
    gray: { 800: '#333333' }
  },
  spacing: {
    small: '0.5rem',
    medium: '1rem',
    large: '1.5rem'
  },
  fonts: { body: 'system-ui' },
  fontSizes: { sm: '0.875rem', md: '1rem', lg: '1.25rem' },
  fontWeights: { medium: '500' },
  lineHeights: { normal: '1.5' },
  radii: { md: '0.25rem' }
};

// Mock App component
const App = () => <div>Mock App</div>;

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <QueryClientProvider>
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything from @testing-library/react
export * from '@testing-library/react';
// Override render method
export { customRender as render };

// Helper function to wait for a specific time
const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Helper function to mock API responses
export const mockApiResponse = (status: number, data: any, ok = true) => {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    clone: function() { return this; },
    headers: new Headers(),
    redirected: false,
    statusText: 'OK',
    type: 'default',
    url: '',
    body: null,
    bodyUsed: false,
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
    blob: () => Promise.resolve(new Blob()),
    formData: () => Promise.resolve(new FormData()),
  });
};

// Helper to generate test data
export const generateTestData = (overrides = {}) => ({
  id: 'test-id',
  name: 'Test Name',
  email: 'test@example.com',
  ...overrides,
});

// Helper to mock window properties
export const mockWindowProperty = (property: string, value: unknown) => {
  const originalProperty = window[property as keyof Window];
  
  beforeAll(() => {
    Object.defineProperty(window, property, {
      value,
      configurable: true,
    });
  });
  
  afterAll(() => {
    Object.defineProperty(window, property, {
      value: originalProperty,
      configurable: true,
    });
  });
};

// Helper to test form field validation
export const testFormField = async (
  { getByLabelText }: { getByLabelText: (label: string) => HTMLElement },
  {
    label,
    value,
    errorMessage,
    type = 'text',
  }: {
    label: string;
    value: string;
    errorMessage?: string;
    type?: string;
  }
) => {
  const input = getByLabelText(label);
  
  // Test that the input is required
  if (errorMessage) {
    fireEvent.change(input, { target: { value: '' } });
    fireEvent.blur(input);
    expect(await screen.findByText(errorMessage)).toBeInTheDocument();
  }
  
  // Test that the input accepts the provided value
  fireEvent.change(input, { target: { value } });
  expect(input).toHaveValue(value);
  
  // Test that the input has the correct type
  expect(input).toHaveAttribute('type', type);
};

// Helper to test async operations
export const waitForApiCall = async (mockFn: jest.Mock) => {
  await wait(0);
  expect(mockFn).toHaveBeenCalled();
};

// Helper to test protected routes
export const testProtectedRoute = async (
  testId: string,
  isAuthenticated: boolean,
  expectedText: string
) => {
  // Use our custom render function that already includes providers
  const { getByTestId, queryByTestId } = render(
    <App />
  );

  if (isAuthenticated) {
    expect(getByTestId(testId)).toHaveTextContent(expectedText);
  } else {
    expect(queryByTestId(testId)).not.toBeInTheDocument();
  }
};

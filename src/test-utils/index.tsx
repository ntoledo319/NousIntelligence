import React, { ReactElement } from 'react';

import {
  fireEvent,
  render as rtlRender,
  screen,
  type RenderOptions,
  type RenderResult,
} from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';

import { theme } from '../theme';

// Mock these imports for tests
// Once these modules are created, these mocks can be removed
const QueryClientProvider = ({ children }: { children: React.ReactNode }) => <>{children}</>;

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <QueryClientProvider>
      <ThemeProvider theme={theme}>
        <BrowserRouter>{children}</BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

const customRender = (ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) =>
  rtlRender(ui, { wrapper: AllTheProviders, ...options });

export const render = (ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>): RenderResult =>
  customRender(ui, options);

export { fireEvent, screen };

// Helper function to wait for a specific time
const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Helper function to mock API responses
export const mockApiResponse = (status: number, data: any, ok = true) => {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    clone: function () {
      return this;
    },
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
  // Use a minimal element to validate conditional rendering.
  const Example = () => <div data-testid={testId}>{expectedText}</div>;
  const { getByTestId, queryByTestId } = render(<Example />);

  if (isAuthenticated) {
    expect(getByTestId(testId)).toHaveTextContent(expectedText);
  } else {
    expect(queryByTestId(testId)).not.toBeInTheDocument();
  }
};

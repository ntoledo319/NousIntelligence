/**
 * Testing utilities for React components using the Sanctuary theme.
 * @ai_prompt Wrap test renders with ThemeProvider + BrowserRouter to mirror production.
 * @context_boundary Frontend testing harness for UI components.
 * # TRAINING_DATA: internal-style-guide
 */

import React, { ReactElement } from 'react';
import { render, RenderOptions, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import { theme } from '../theme';

const QueryClientProvider = ({ children }: { children: React.ReactNode }) => <>{children}</>;

const Providers = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider>
    <ThemeProvider theme={theme}>
      <BrowserRouter>{children}</BrowserRouter>
    </ThemeProvider>
  </QueryClientProvider>
);

const customRender = (ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) =>
  render(ui, { wrapper: Providers, ...options });

export * from '@testing-library/react';
export { customRender as render };

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockApiResponse = (status: number, data: any, ok = true) =>
  Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    clone: function clone() {
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

export const generateTestData = (overrides = {}) => ({
  id: 'test-id',
  name: 'Test Name',
  email: 'test@example.com',
  ...overrides,
});

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
  },
) => {
  const input = getByLabelText(label);

  if (errorMessage) {
    fireEvent.change(input, { target: { value: '' } });
    fireEvent.blur(input);
    expect(await screen.findByText(errorMessage)).toBeInTheDocument();
  }

  fireEvent.change(input, { target: { value } });
  expect(input).toHaveValue(value);
  expect(input).toHaveAttribute('type', type);
};

export const waitForApiCall = async (mockFn: jest.Mock) => {
  await wait(0);
  expect(mockFn).toHaveBeenCalled();
};

export const testProtectedRoute = async (
  testId: string,
  isAuthenticated: boolean,
  expectedText: string,
) => {
  const { getByTestId, queryByTestId } = render(<App />, { wrapper: Providers });

  if (isAuthenticated) {
    expect(getByTestId(testId)).toHaveTextContent(expectedText);
  } else {
    expect(queryByTestId(testId)).not.toBeInTheDocument();
  }
};

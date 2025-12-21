import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import App from '../App';

describe('App routing + safety', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
    window.history.pushState({}, 'Test', '/');
  });

  it('navigates to Mood via URL', async () => {
    window.history.pushState({}, 'Mood', '/mood');
    render(<App />);
    expect(screen.getByText(/How are you doing, 1–10\?/i)).toBeInTheDocument();
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
  });

  it('opens the Safety layer and lists crisis resources', async () => {
    (global.fetch as jest.Mock).mockImplementation((input: RequestInfo) => {
      const url = typeof input === 'string' ? input : (input as any)?.url || '';
      if (url.includes('/resources/api/crisis')) {
        const payload = {
          resources: [
            {
              name: '988 Lifeline',
              description: 'US Suicide & Crisis Lifeline',
              phone_number: '988',
              text_number: '988',
            },
          ],
        };
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(payload),
          json: async () => payload,
        } as any);
      }
      if (url.includes('/api/v2/safety-plan')) {
        const payload = { ok: true, plan: null };
        return Promise.resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(payload),
          json: async () => payload,
        } as any);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        text: async () => '{}',
        json: async () => ({}),
      } as any);
    });

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Need help now?' }));

    expect(screen.getByRole('dialog', { name: 'Safety and crisis support' })).toBeInTheDocument();
    expect(await screen.findByText('988 Lifeline')).toBeInTheDocument();
    expect(screen.getByText(/Call:\s*988/i)).toBeInTheDocument();
  });
});

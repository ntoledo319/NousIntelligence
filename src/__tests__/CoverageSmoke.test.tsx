import { fireEvent, render, screen } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';

import App from '../App';
import { Chip, PrimaryButton, SecondaryButton, SegmentedControl } from '../components/ui';
import { theme } from '../theme';

describe('coverage smoke', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
  });

  it('renders button wrappers and chip', () => {
    render(
      <ThemeProvider theme={theme}>
        <PrimaryButton>Primary</PrimaryButton>
        <SecondaryButton>Secondary</SecondaryButton>
        <Chip selected>Sleep</Chip>
      </ThemeProvider>
    );

    expect(screen.getByText('Primary')).toBeInTheDocument();
    expect(screen.getByText('Secondary')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sleep' })).toHaveAttribute('aria-pressed', 'true');
  });

  it('segmented control toggles', () => {
    const onChange = jest.fn();
    render(
      <ThemeProvider theme={theme}>
        <SegmentedControl
          aria-label='Mode'
          value='gentle'
          onChange={onChange}
          options={[
            { value: 'gentle', label: 'Gentle' },
            { value: 'structured', label: 'Structured' },
          ]}
        />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Structured' }));
    expect(onChange).toHaveBeenCalledWith('structured');
  });

  it('renders remaining routes (journal, talk, more)', () => {
    window.history.pushState({}, 'Journal', '/journal');
    const r1 = render(<App />);
    expect(screen.getByText(/What’s on your mind\?/i)).toBeInTheDocument();
    r1.unmount();

    window.history.pushState({}, 'Talk', '/talk');
    const r2 = render(<App />);
    expect(screen.getByLabelText('Conversation')).toBeInTheDocument();
    r2.unmount();

    window.history.pushState({}, 'More', '/more');
    render(<App />);
    expect(screen.getByText(/Experience mode/i)).toBeInTheDocument();
  });

  it('covers key flows: mood save, journal save, guided thought record, chat send, export', async () => {
    // Mood save
    window.history.pushState({}, 'Mood', '/mood');
    const m = render(<App />);
    fireEvent.change(screen.getByLabelText(/Mood rating/i), { target: { value: '7' } });
    fireEvent.change(screen.getByPlaceholderText(/A sentence or two is enough/i), {
      target: { value: 'tough day' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Save check-in/i }));
    expect(await screen.findByText(/Saved\./i)).toBeInTheDocument();
    m.unmount();

    // Journal free write save
    window.history.pushState({}, 'Journal', '/journal');
    const j = render(<App />);
    fireEvent.change(screen.getByPlaceholderText(/Start with one sentence/i), {
      target: { value: 'hello' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save' }));
    expect(await screen.findByText(/Saved just now/i)).toBeInTheDocument();

    // Guided thought record
    fireEvent.click(screen.getByRole('button', { name: 'Guided tools' }));
    fireEvent.change(screen.getByPlaceholderText(/What happened\?/i), {
      target: { value: 'argument' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    fireEvent.change(screen.getByPlaceholderText(/What did your mind say/i), {
      target: { value: 'I am terrible' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    fireEvent.change(screen.getByLabelText('Emotions'), { target: { value: 'sad' } });
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    fireEvent.click(screen.getByRole('button', { name: /Save thought record/i }));
    expect(await screen.findByText(/Saved\./i)).toBeInTheDocument();
    j.unmount();

    // Talk send
    window.history.pushState({}, 'Talk', '/talk');
    const t = render(<App />);
    fireEvent.change(screen.getByLabelText('Message'), { target: { value: 'hi' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send' }));
    expect(await screen.findByText('ok')).toBeInTheDocument();
    t.unmount();

    // Export
    window.history.pushState({}, 'More', '/more');
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        text: async () => JSON.stringify({ ok: true, text: 'EXPORT' }),
        json: async () => ({ ok: true, text: 'EXPORT' }),
      } as any)
    );
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Generate' }));
    expect(await screen.findByDisplayValue('EXPORT')).toBeInTheDocument();
  });

  it('covers SafetySheet error path', async () => {
    (global.fetch as jest.Mock).mockImplementation((input: RequestInfo) => {
      const url = typeof input === 'string' ? input : (input as any)?.url || '';
      if (url.includes('/resources/api/crisis')) {
        const payload = { error: 'nope' };
        return Promise.resolve({
          ok: false,
          status: 500,
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

    window.history.pushState({}, 'Home', '/');
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Need help now?' }));
    expect(await screen.findByText(/Couldn’t load resources/i)).toBeInTheDocument();
  });
});

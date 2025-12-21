import { render, screen, waitFor } from '@testing-library/react';

import App from '../App';

describe('App', () => {
  it('renders Harbor home route', async () => {
    render(<App />);
    expect(screen.getByText('How’s the weather inside today?')).toBeInTheDocument();
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
  });
});

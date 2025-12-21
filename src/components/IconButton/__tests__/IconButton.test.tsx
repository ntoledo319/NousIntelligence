import { render, screen, fireEvent } from '../../../test-utils';
import IconButton from '../IconButton';

describe('IconButton', () => {
  it('renders an icon-only button with aria-label', () => {
    render(<IconButton ariaLabel='Need help now' icon={<span>?</span>} />);
    const btn = screen.getByTestId('icon-button');
    expect(btn).toBeInTheDocument();
    expect(btn).toHaveAttribute('aria-label', 'Need help now');
  });

  it('supports size variants (small and large)', () => {
    const { rerender } = render(
      <IconButton ariaLabel='Small' icon={<span>S</span>} size='small' />
    );
    expect(screen.getByTestId('icon-button')).toBeInTheDocument();

    rerender(<IconButton ariaLabel='Large' icon={<span>L</span>} size='large' />);
    expect(screen.getByTestId('icon-button')).toBeInTheDocument();
  });

  it('forwards onClick', () => {
    const onClick = jest.fn();
    render(<IconButton ariaLabel='Click' icon={<span>+</span>} onClick={onClick} />);
    fireEvent.click(screen.getByTestId('icon-button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
